from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, Product, Customer

class CreateOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'customer', 'quantity', 'price', 'address', 'phone']

class CreateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'digital', 'image', 'out_of_order']

# form to create the related Customer model during registration
class CreateCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'password']

# user creation form (wraps Django's built-in form)
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']