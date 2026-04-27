from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import HttpResponse
import random
from django.core.mail import send_mail
from django.http import JsonResponse
from .models import EmailOTP
from django.contrib.auth.models import User

# try to import the helper from the verify_email package; provide a simple fallback
try:
    from verify_email.email_handler import send_verification_email
except Exception:
    # fallback implementation that sends a simple console email (works with console email backend)
    from django.core.mail import send_mail

    def send_verification_email(request, form):
        """
        Minimal fallback: attempt to get an email from the form and send a basic message.
        Returns True on success, None/False on failure.
        """
        try:
            email = ''
            # prefer cleaned_data when available
            if hasattr(form, 'cleaned_data'):
                email = form.cleaned_data.get('email') or form.cleaned_data.get('username') or ''
            else:
                email = form.data.get('email') or form.data.get('username') or ''
            if not email:
                return None
            send_mail(
                subject='Verify your email',
                message='Please verify your account. (fallback email)',
                from_email=None,
                recipient_list=[email],
                fail_silently=True,
            )
            return True
        except Exception:
            return None

from .models import Product, Customer, Order
from .forms import CreateOrderForm, CreateProductForm, CreateCustomerForm, CreateUserForm

def home(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    # use homepage.html (existing template) instead of website/homepage.html
    return render(request, 'homepage.html', context)


def placeOrder(request, i):
    customer = Customer.objects.get(id=i)
    form = CreateOrderForm()

    if request.method == 'POST':
        form = CreateOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = customer
            order.save()
            return redirect('/')

    context = {'form': form}
    return render(request, 'placeOrder.html', context)


def addProduct(request):
    form = CreateProductForm()

    if request.method == 'POST':
        form = CreateProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}
    return render(request, 'addProduct.html', context)


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        user.save()
        messages.success(request, "Account created successfully")
        return redirect("login")

    return render(request, "signup.html")

def product_list(request):
    query = request.GET.get('q', '').strip()
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'product_list.html', context)

def view_cart(request):
    # delegate to the cart app's view which uses the SQL Cart/CartItem models
    return redirect('cart:view_cart')

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            username_or_email = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username_or_email, password=password)

            if user is None:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                login(request, user)
                return redirect('/')

        context = {}
        return render(request, 'login.html', context)


def logoutPage(request):
    logout(request)
    return redirect('/')


def forgot_password(request):
    return render(request, 'forgot_password.html')


def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            inactive_user = send_verification_email(request, form)

            if inactive_user:
                return HttpResponse('Please check your email to verify your account.')

        else:
            print(form.errors)  # 👈 DEBUG

    else:
        form = RegisterForm()

    return render(request, "signup.html", {"form": form})

def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not Customer.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email not registered.'}, status=400)
        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(email=email, defaults={'otp': otp})
        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP code is {otp}',
            from_email=None,
            recipient_list=[email],
            fail_silently=True,
        )
        return JsonResponse({'message': 'OTP sent to email.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        password = request.POST.get('password')

        record = EmailOTP.objects.filter(email=email, otp=otp).last()

        if record:
            try:
                customer = Customer.objects.get(email=email)
                user = customer.user
                user.set_password(password)
                user.save()
                EmailOTP.objects.filter(email=email).delete()
                return JsonResponse({'message': 'Password reset successful.'})
            except Customer.DoesNotExist:
                return JsonResponse({'error': 'User not found.'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid OTP.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


# Admin Dashboard
def admin_dashboard(request):
    """Admin dashboard showing overview of customers, orders, and products"""
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    completed_orders = Order.objects.filter(status=True).count()
    pending_orders = Order.objects.filter(status=False).count()
    total_revenue = sum([order.price * order.quantity for order in Order.objects.all()])
    
    recent_orders = Order.objects.all().order_by('-date')[:10]
    recent_customers = Customer.objects.all().order_by('-id')[:10]
    
    context = {
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_products': total_products,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'recent_customers': recent_customers,
    }
    return render(request, 'admin_dashboard.html', context)


def admin_orders(request):
    """Admin view for managing orders"""
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    orders = Order.objects.all().order_by('-date')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        status_filter = status_filter.lower() == 'completed'
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
    }
    return render(request, 'admin_orders.html', context)


def admin_customers(request):
    """Admin view for managing customers"""
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    customers = Customer.objects.all().order_by('-id')
    context = {
        'customers': customers,
    }
    return render(request, 'admin_customers.html', context)


def admin_products(request):
    """Admin view for managing products"""
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'admin_products.html', context)


def toggle_product_status(request, product_id):
    """Toggle the out-of-order status for a product"""
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to change product status.")
        return redirect('admin_products')

    product = get_object_or_404(Product, id=product_id)
    product.out_of_order = not product.out_of_order
    product.save()
    return redirect('admin_products')


def update_order_status(request, order_id):
    """Update order status to completed"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        order = Order.objects.get(id=order_id)
        order.status = not order.status
        order.save()
        return JsonResponse({'message': 'Order status updated successfully.'})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found.'}, status=404)


# User Profile/Dashboard
def user_profile(request):
    """User profile page showing order history and profile info"""
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to view your profile.")
        return redirect('login')
    
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        messages.error(request, "Customer profile not found.")
        return redirect('home')
    
    orders = Order.objects.filter(customer=customer).order_by('-date')
    latest_order = orders.first()
    
    context = {
        'customer': customer,
        'orders': orders,
        'latest_order': latest_order,
    }
    return render(request, 'user_profile.html', context)


def update_profile(request):
    """Update user profile information"""
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to update your profile.")
        return redirect('login')
    
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        messages.error(request, "Customer profile not found.")
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        if not name or not email:
            messages.error(request, "Name and email are required.")
            return redirect('user_profile')
        
        # Check if email is already taken by another user
        if email != customer.email and Customer.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return redirect('user_profile')
        
        customer.name = name
        customer.email = email
        customer.phone = phone
        customer.user.email = email
        customer.save()
        customer.user.save()
        
        messages.success(request, "Profile updated successfully.")
        return redirect('user_profile')
    
    context = {
        'customer': customer,
    }
    return render(request, 'update_profile.html', context)


def repurchase_order(request, order_id):
    """Repurchase items from a previous order"""
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to repurchase.")
        return redirect('login')
    
    try:
        customer = Customer.objects.get(user=request.user)
        original_order = Order.objects.get(id=order_id, customer=customer)
    except (Customer.DoesNotExist, Order.DoesNotExist):
        messages.error(request, "Order not found.")
        return redirect('user_profile')
    
    # Create a new order with the same product and quantity
    new_order = Order(
        product=original_order.product,
        customer=customer,
        quantity=original_order.quantity,
        price=original_order.price,
        address=original_order.address,
        phone=original_order.phone,
        status=False
    )
    new_order.save()
    
    messages.success(request, f"Successfully repurchased {original_order.product.name}. New order created!")
    return redirect('user_profile')
