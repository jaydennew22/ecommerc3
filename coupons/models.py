from django.db import models
from django.utils import timezone

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()
    discount_percentage = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}%)"
