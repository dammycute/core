from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Property)
# admin.site.register(Order)
admin.site.register(Investment)
admin.site.register(Wallet)
admin.site.register(Transaction)


