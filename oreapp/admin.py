from django.contrib import admin
from .models import Menu,User,Order
# Register your models here.

admin.site.register(Menu)
admin.site.register(Order)
admin.site.register(User)