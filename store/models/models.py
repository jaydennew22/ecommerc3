from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator


#create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone= models.CharField(max_length=15, null=True, blank=True)
    password = models.CharField(max_length=200, null=True)

#save customer
    def register(self):
        self.save()

    @staticmethod
    def get_customer_by_email(email):
        try:
            return Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return False

    def isExists(self):
        return Customer.objects.filter(email=self.email).exists()
    
    class Meta:
        verbose_name_plural = 'Customers'

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True, blank=True)
    out_of_order = models.BooleanField(default=False)

    @staticmethod
    def get_products_by_id(ids):
        return Product.objects.filter(id__in=ids)

    @staticmethod
    def get_all_products():
        return Product.objects.all()

    @staticmethod
    def get_all_products_by_categoryid(category_id):
        if not category_id:
            return Product.get_all_products()
        try:
            return Product.objects.filter(category=category_id)
        except Exception:
            return Product.get_all_products()

    def __str__(self):
        return self.name if self.name else ''

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()
    address = models.CharField(max_length=50, default='', blank=True)
    phone = models.CharField(max_length=50, default='', blank=True)
    date = models.DateField(default=datetime.date.today) 
    status = models.BooleanField(default=False)

    def placeOrder(self):
        self.save()

    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.objects.filter(customer=customer_id).order_by('-date')

    class Meta:
        verbose_name_plural = "Orders"

    def __str__(self):
        return str(self.id)



class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def __str__(self):
        return self.code
    

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.order.id}"


class EmailOTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email