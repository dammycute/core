from django.db import models
from django.conf import settings
from django.utils import timezone
from business.models import *
import datetime
from cloudinary_storage.storage import RawMediaCloudinaryStorage


class MyCloudinaryStorage(RawMediaCloudinaryStorage):
    folder = "property/images"


# Create your models here.
class Property(models.Model):
    CHOICES = (
        ('Real Asset', 'Real Asset'),
        ('Real Banking', 'Real Banking'),
        ('Real Project', 'Real Project'),

    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    property_name = models.CharField(max_length=255, null=True)
    category = models.CharField(max_length=200, choices= CHOICES, null=True)
    duration = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    roi = models.DecimalField(null=True, max_digits=5, decimal_places=2)
    price_per_slot = models.DecimalField(null=True, max_digits=15, decimal_places=2)
    location = models.CharField(max_length=300, null=True)
    amount = models.CharField(max_length=255, null=True)
    image1 = models.ImageField(upload_to='images/', null=True, blank=True, storage=MyCloudinaryStorage())
    image2 = models.ImageField(upload_to='images/', null=True, blank=True, storage=MyCloudinaryStorage())
    image3 = models.ImageField(upload_to='images/', null=True, blank=True, storage=MyCloudinaryStorage())
    slots_available = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    terms_and_condition = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.property_name

    class Meta:
        verbose_name_plural = "Property"


    
class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    amount = models.FloatField()
    reference = models.CharField(max_length=100)
    status = models.CharField(max_length=20)

    def __str__(self):
        return str(self.balance)
    
    # class Investment(models.Model):
    #     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    #     user_property = models.ForeignKey(Property, null=True, on_delete=models.CASCADE)


class Order(models.Model):
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_FAILED = 'F'

    PAYMENT_STATUS_CHOICES = (
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    )
    customer = models.ForeignKey(CustomerDetails, null=True, on_delete=models.CASCADE)
    # product = models.ForeignKey(Property, null=True, on_delete=models.PROTECT)
    Date_purchased = models.DateTimeField(auto_now_add=True)
    Due_Date = models.DateTimeField(default = timezone.now, blank = True)
    payment_status = models.CharField(max_length=1, choices = PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)

    def __str__(self):
        return 'Order'
    # class Meta:
        # verbose_name_plural = "Customer_Prop"

class Investment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Property, null=True, on_delete=models.CASCADE)
    slots = models.PositiveBigIntegerField(null=True)
    current_value = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # is_agreed = models.BooleanField(default=False)

    # def save(self, *args, **kwargs):
    #     # Calculate the number of months since the investment started
    #     today = datetime.date.today()
    #     elapsed_months = (today.year - self.start_date.year) * 12 + (today.month - self.start_date.month)

    #     # Calculate the current value based on the number of elapsed months and the investment's ROI
    #     current_value = self.total_price * (1 + ((self.roi / 12) / 100) * elapsed_months)

    #     # Update the current value field of the investment object
    #     self.current_value = current_value

    #     # Save the investment object
    #     super().save(*args, **kwargs)

    def calculate_roi(self, date):
        days_since_start = (date - self.start_date).days
        months_since_start = int(days_since_start / 30)
        roi = self.product.roi * months_since_start
        return roi


