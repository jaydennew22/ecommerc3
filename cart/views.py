from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from store.models.models import Product, Customer, Order
from coupons.models import Coupon
from .models import Cart, CartItem
from .forms import CheckoutForm
from django.db import transaction

def _get_or_create_cart(request):
    # prefer user cart when logged in, otherwise session-backed cart record
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            customer = None
        if customer:
            cart, _ = Cart.objects.get_or_create(customer=customer)
            return cart
    session_cart_id = request.session.get('cart_id')
    if session_cart_id:
        try:
            return Cart.objects.get(id=session_cart_id)
        except Cart.DoesNotExist:
            pass
    cart = Cart.objects.create(session_key=request.session.session_key or None)
    request.session['cart_id'] = cart.id
    return cart

def product_list(request):
    # simple redirect to the main store; keep for compatibility
    return redirect('home')

def add_to_cart(request, product_id):
    # supports POST quantity or GET param 'qty'
    qty = 1
    if request.method == 'POST':
        try:
            qty = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            qty = 1
    else:
        try:
            qty = int(request.GET.get('qty', 1))
        except (TypeError, ValueError):
            qty = 1
    if qty < 1:
        qty = 1
    if qty > 100:
        qty = 100

    product = get_object_or_404(Product, id=product_id)
    if getattr(product, 'out_of_order', False):
        return redirect('products')

    cart = _get_or_create_cart(request)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': qty})
    if not created:
        item.quantity = item.quantity + qty
        item.save()

    return redirect('cart:view_cart')

def update_quantity(request, cartitem_id):
    if request.method != 'POST':
        return redirect('cart:view_cart')
    
    try:
        item = CartItem.objects.get(id=cartitem_id)
    except CartItem.DoesNotExist:
        return redirect('cart:view_cart')
    
    action = request.POST.get('action', '')
    
    if action == 'increase':
        if item.quantity < 100:
            item.quantity += 1
            item.save()
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    else:
        # Fallback: direct quantity update
        try:
            qty = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            qty = 1
        
        if qty < 1:
            item.delete()
        else:
            if qty > 100:
                qty = 100
            item.quantity = qty
            item.save()
    
    return redirect('cart:view_cart')

def remove_from_cart(request, product_id):
    cart = _get_or_create_cart(request)
    CartItem.objects.filter(cart=cart, product_id=product_id).delete()
    return redirect('cart:view_cart')

def view_cart(request):
    cart = _get_or_create_cart(request)
    qs = cart.items.select_related('product').all()
    items = []
    total = Decimal('0.00')
    for it in qs:
        price = Decimal(str(it.product.price or 0))
        subtotal = (price * it.quantity).quantize(Decimal('0.01'))
        items.append({
            'product': it.product,
            'quantity': it.quantity,
            'subtotal': subtotal,
            'cartitem_id': it.id,
        })
        total += subtotal
    context = {'cart': cart, 'cart_items': items, 'total_price': total}
    return render(request, 'cart.html', context)

@login_required(login_url=reverse_lazy('login'))
@transaction.atomic
def checkout(request):
    cart = _get_or_create_cart(request)
    
    # Handle item actions (increase, decrease, remove)
    if request.method == 'POST' and 'item_id' in request.POST:
        action = request.POST.get('action', '')
        item_id = request.POST.get('item_id', '')
        
        if action in ['increase', 'decrease', 'remove']:
            try:
                item = CartItem.objects.get(id=item_id, cart=cart)
                if action == 'increase':
                    item.quantity += 1
                    item.save()
                elif action == 'decrease':
                    if item.quantity > 1:
                        item.quantity -= 1
                        item.save()
                    else:
                        item.delete()
                elif action == 'remove':
                    item.delete()
            except CartItem.DoesNotExist:
                pass
            return redirect('cart:view_cart')
    
    qs = cart.items.select_related('product').all()
    if not qs.exists():
        return redirect('cart:view_cart')

    items = []
    subtotal = Decimal('0.00')
    for it in qs:
        p = it.product
        line_total = Decimal(str(p.price or 0)) * it.quantity
        items.append({'cartitem': it, 'product': p, 'quantity': it.quantity, 'line_total': line_total, 'id': it.id})
        subtotal += line_total

    coupon_obj = None
    discount_amount = Decimal('0.00')
    coupon_error = ''

    if request.method == 'POST':
        action = request.POST.get('action', 'checkout')
        coupon_code = request.POST.get('coupon_code', '').strip()
        form = CheckoutForm(request.POST)

        if coupon_code:
            try:
                c = Coupon.objects.get(code__iexact=coupon_code, active=True)
                now = timezone.now()
                if c.valid_from <= now <= c.valid_to:
                    coupon_obj = c
                    discount_amount = (subtotal * Decimal(c.discount_percentage) / Decimal(100)).quantize(Decimal('0.01'))
                else:
                    coupon_obj = None
                    coupon_error = 'Coupon expired or not valid.'
            except Coupon.DoesNotExist:
                coupon_obj = None
                coupon_error = 'Coupon code not found.'
        elif action == 'apply':
            coupon_error = 'Please enter a coupon code.'

        if action == 'apply':
            # just re-render with coupon applied
            pass
        elif action == 'checkout' and form.is_valid():
            # build or find customer
                if request.user.is_authenticated:
                    try:
                        customer = Customer.objects.get(user=request.user)
                    except Customer.DoesNotExist:
                        # create a Customer record from provided name/email if possible
                        customer, _ = Customer.objects.get_or_create(
                            name=form.cleaned_data.get('name') or 'Guest',
                            email=form.cleaned_data.get('email') or '',
                            defaults={'phone': form.cleaned_data.get('phone','')}
                        )
                else:
                    # guest checkout: create or get customer by email if provided
                    customer, _ = Customer.objects.get_or_create(
                        email=form.cleaned_data.get('email') or None,
                        defaults={'name': form.cleaned_data.get('name') or 'Guest', 'phone': form.cleaned_data.get('phone','')}
                    )

                # ensure a customer exists (if Customer model requires fields, adjust accordingly)
                if not customer:
                    return redirect('register')

                total_discount = discount_amount
                for entry in items:
                    line_total = entry['line_total']
                    line_discount = (line_total / subtotal * total_discount) if subtotal > 0 else Decimal('0.00')
                    line_price_after = (line_total - line_discount).quantize(Decimal('0.01'))
                    Order.objects.create(
                        product=entry['product'],
                        customer=customer,
                        quantity=entry['quantity'],
                        price=int((line_price_after * 100)),  # cents - adjust if you change Order.price
                        address=form.cleaned_data.get('address'),
                        phone=form.cleaned_data.get('phone'),
                        status=False,
                    )
                cart.items.all().delete()
                return redirect('cart:checkout_success')
    else:
        form = CheckoutForm()

    context = {
        'cart': cart,
        'items': items,
        'subtotal': subtotal,
        'coupon': coupon_obj,
        'discount': discount_amount,
        'total': (subtotal - discount_amount).quantize(Decimal('0.01')),
        'form': form,
        'coupon_error': coupon_error,
    }
    return render(request, 'cart/checkout.html', context)

# similarly for checkout_success:
@login_required(login_url=reverse_lazy('login'))
def checkout_success(request):
    return render(request, 'cart/success.html')

# run at PowerShell prompt:
# python manage.py shell
#
# then inside Python REPL:
# from cart.models import Cart, CartItem
# from store.models.models import Product
# Cart.objects.count(), CartItem.objects.count()
# # create test cart/item:
# c = Cart.objects.create()
# p = Product.objects.first()
# CartItem.objects.create(cart=c, product=p, quantity=2)