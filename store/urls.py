from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.home, name='home'),
    path('placeOrder/<int:i>/', views.placeOrder, name='placeOrder'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('register/', views.signup, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('addproduct/', views.addProduct, name='addproduct'),
    path('products/', views.product_list, name='products'),
    path('cart/', include('cart.urls', namespace='cart')),  # added cart routes
    # Removed verify-email include because the verify_email package does not expose URL routes
    path('send-otp/', views.send_otp, name='send_otp'),  # added OTP sending route
    path('reset-password/', views.reset_password, name='reset_password'),  # added password reset route
    
    # Admin Dashboard URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('admin-customers/', views.admin_customers, name='admin_customers'),
    path('admin-products/', views.admin_products, name='admin_products'),
    path('admin-products/toggle-status/<int:product_id>/', views.toggle_product_status, name='toggle_product_status'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    
    # User Profile URLs
    path('profile/', views.user_profile, name='user_profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('repurchase/<int:order_id>/', views.repurchase_order, name='repurchase_order'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
