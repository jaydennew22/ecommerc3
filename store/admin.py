from django.contrib import admin

# import models from the nested module; CartItem may be absent, handle gracefully
try:
    from .models.models import Customer, Product, Order, CartItem
except Exception:
    from .models.models import Customer, Product, Order
    CartItem = None


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone')
    search_fields = ('name', 'email')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'digital', 'out_of_order')
    search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'customer', 'quantity', 'price', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('customer__name', 'product__name')


# only register CartItem if it exists to avoid NameError
if CartItem is not None:
    admin.site.register(CartItem)