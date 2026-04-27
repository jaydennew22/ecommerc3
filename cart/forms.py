from django import forms

class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    address = forms.CharField(max_length=255, required=True)
    phone = forms.CharField(max_length=30, required=True)
    coupon_code = forms.CharField(max_length=50, required=False)
    # hidden field to indicate action ('apply' or 'checkout')
    action = forms.CharField(max_length=16, required=False, widget=forms.HiddenInput())