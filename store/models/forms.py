from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username',
            'class': 'form-input'
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Email Address',
            'class': 'form-input'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password',
            'class': 'form-input'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm Password',
            'class': 'form-input'
        })

class CreateOrderForm(ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['status']

class CreateProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class CreateCustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['phone'].required = False
        self.fields['name'].widget.attrs.update({
            'placeholder': 'Name (optional)',
            'class': 'form-input'
        })
        self.fields['phone'].widget.attrs.update({
            'placeholder': 'Phone (optional)',
            'class': 'form-input'
        })