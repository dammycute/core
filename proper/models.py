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

    def __str__(self):
        return str(self.balance)


class Transaction(models.Model):
    PENDING = 'Pending'
    COMPLETED = 'Completed'
    FAILED = 'Failed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]
    
    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True)
    customer= models.ForeignKey(CustomerDetails, on_delete=models.CASCADE,  null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    tx_ref = models.CharField(max_length=50, unique=True, null=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=True)
    payment_type = models.CharField(max_length=50, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return str(self.tx_ref)



class Investment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Property, null=True, on_delete=models.CASCADE)
    slots = models.PositiveBigIntegerField(null=True)
    current_value = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def calculate_roi(self, date):
        days_since_start = (date - self.start_date).days
        months_since_start = int(days_since_start / 30)
        roi = self.product.roi * months_since_start
        return roi


class BankAccount(models.Model):
    BANK_CHOICES = (
        ('access', 'Access Bank'),
        ('citibank', 'Citibank'),
        ('diamond', 'Diamond Bank'),
        ('ecobank', 'Ecobank'),
        ('fidelity', 'Fidelity Bank'),
        ('first_bank', 'First Bank'),
        ('fcmb', 'First City Monument Bank'),
        ('gtb', 'Guaranty Trust Bank'),
        ('heritage', 'Heritage Bank'),
        ('keystone', 'Keystone Bank'),
        ('polaris', 'Polaris Bank'),
        ('providus', 'Providus Bank'),
        ('stanbic', 'Stanbic IBTC Bank'),
        ('standard_chartered', 'Standard Chartered Bank'),
        ('sterling', 'Sterling Bank'),
        ('suntrust', 'Suntrust Bank'),
        ('union', 'Union Bank'),
        ('uba', 'United Bank for Africa'),
        ('unity', 'Unity Bank'),
        ('wema', 'Wema Bank'),
        ('zenith', 'Zenith Bank'),
        ('alat', 'ALAT by WEMA'),
        ('jubilee', 'Jubilee Bank'),
        ('sparkle', 'Sparkle'),
        ('kuda', 'Kuda Bank'),
        ('opay', 'OPay'),
        ('palmpay', 'PalmPay'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=10)
    
    # bank_code = models.CharField(max_length=10, blank=True)
    amount = models.CharField(max_length=10)
    bank = models.CharField(choices=BANK_CHOICES, max_length=50)

    def __str__(self):
        return f"{self.user.username}'s {self.bank} Account ({self.account_number})"



# class BankAccount(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     account_number = models.CharField(max_length=20)
#     bank_code = models.CharField(max_length=10)
#     account_name = models.CharField(max_length=255)
