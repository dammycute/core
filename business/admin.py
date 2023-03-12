from django.contrib import admin

# Register your models here.

from .models import *

# admin.register()
admin.site.register(CustomUser)
admin.site.register(CustomerDetails)
# admin.site.register(Bvn)
# admin.site.register(Nin)
# admin.site.register(Security)
# admin.site.register(Picture)

