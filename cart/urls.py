from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('view/', views.view_cart, name='view_cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update/<int:cartitem_id>/', views.update_quantity, name='update_quantity'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.checkout_success, name='checkout_success'),
]