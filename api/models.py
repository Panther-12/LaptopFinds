from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import random

# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title
    
class Products(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    description = models.TextField(blank=True)
    vendor = models.ForeignKey(User, on_delete=models.PROTECT)
    fixed_price = models.BooleanField(default=True)
    inventory = models.IntegerField(default=1)

    def __str__(self):
        return self.name

class Orders(models.Model):
    secret = models.CharField(max_length=1000, default="", blank=True)
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.TextField()
    total = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.BooleanField(default=False) # After successful checkout the status is changed to True/Paid
    date = models.DateField(default=now())
    cancelled_status = models.BooleanField(default=False)
    checkout_url = models.CharField(max_length=1000, default="", blank=True)

    def __str__(self):
        return self.products
    
    def generate_secret(self):
        self.secret = str(random.randint(10000, 99999))
    
    
class Offers(models.Model):
    _from = models.ForeignKey(User, on_delete=models.PROTECT)
    product = models.ForeignKey(Products, on_delete=models.PROTECT)
    offer_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    state = models.BooleanField(default=False) # After the state is updated to True or closed, the amount on the cart is also updated
    date = models.DateField(default=now())
    counter_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __str__(self):  
        return str(self.counter_amount)
    
    
class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    product = models.ForeignKey(Products, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    def __str__(self):
        return self.product
    
    def setAmount(self,):
        self.amount = self.product.price
        return self.amount

    
    def generateCart(self,customerId):
        products = Cart.objects.filter(customer=customerId)
        if len(products) <=0 :
            return "cart is empty"
        cart_products = []
        for product in products:
            details = Products.objects.get(pk=product.product.pk)
            cart_products.append({"product_name":details.name, "product_id":details.pk, "vendor_id":details.vendor.pk, "vendor_name":details.vendor.username, "quantity_left":details.inventory,"price":product.amount, "quantity":product.quantity})
        return cart_products
    

class VendorOrders(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=1)
    customer_name = models.CharField(max_length=255, null=True)
    customer_phone = models.CharField(max_length=255, null=True)
    paid_status = models.BooleanField(default=False)
    delivery_status = models.BooleanField(default=False)
    cancelled_status = models.BooleanField(default=False)
    date = models.DateField(default=now())

    def __str__(self):
        return self.product_name
    
# class reviews(models.Model):
#     pass

# class Followers(models.Model):
#     pass

# class Following(models.Model):
#     pass