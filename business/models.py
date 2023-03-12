from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.conf import settings
from cloudinary_storage.storage import RawMediaCloudinaryStorage

# from django.forms import BooleanField, DateField, ImageField

class UserManager(BaseUserManager):
    """ User Manager that knows how to create users via email instead of username """
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(verbose_name='date joined', default = timezone.now, blank = True)
    last_login_time = models.DateTimeField(verbose_name='last login', default = timezone.now, blank = True)
    

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    

    def __str__(self):
        return self.email


# class UserActivation(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, unique= True)
#     activation_pin = models.CharField(max_length=10)
#     expiry_date = models.DateTimeField()


class CustomerDetails(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, unique= True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=70, null=True)
    state = models.CharField(max_length=100, null=True)
    zipcode = models.IntegerField(null=True)
    birth_date = models.DateField(null=True, blank=True)
    # bvn = models.IntegerField(null=True)
    nin = models.IntegerField(null=True)
    fpage = models.ImageField(upload_to='images/', null=True, blank=True, storage=RawMediaCloudinaryStorage())
    bpage = models.ImageField(upload_to='images/', null=True, blank=True, storage=RawMediaCloudinaryStorage())
    security_question = models.CharField(max_length=255, null=True)
    security_answer = models.CharField(max_length=255, null=True)
    picture = models.ImageField(upload_to='images/', null=True, blank=True, storage=RawMediaCloudinaryStorage())
    
    def name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name_plural = "Customer Details"

# class Bvn(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, unique= True)
    
    
#     def __str__(self):
#         return self.bvn
    
#     class Meta:
#         verbose_name_plural = "Bvn"
    


# class Nin(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, unique= True)

#     def __str__(self):
#         return self.nin

#     class Meta:
#         verbose_name_plural = "Nin"

    

# class Security(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, unique= True)
    

#     def __str__(self):
#         return self.security_question

#     class Meta:
#         verbose_name_plural = "Security Details"

# class Picture(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, unique= True)
    

#     def __str__(self):
#         return self.picture

#     class Meta:
#         verbose_name_plural = "Picture"
