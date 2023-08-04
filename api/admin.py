from django.contrib import admin
from .models import Category, Products, Cart, VendorOrders, Orders, Offers

# Register your models here.
admin.site.register(Category)
admin.site.register(Products)
admin.site.register(Cart)
admin.site.register(VendorOrders)
admin.site.register(Offers)
admin.site.register(Orders)