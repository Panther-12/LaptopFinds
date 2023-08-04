from rest_framework import serializers
from .models import Category, Products, Cart, VendorOrders, Orders, Offers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    vendor = UserSerializer(read_only=True)
    vendor_id = serializers.IntegerField(write_only=True)
    class Meta:
        model= Products
        fields = ['id', 'category', 'category_id', 'vendor_id', 'vendor','name', 'price', 'description', 'fixed_price', 'inventory']

class CreateProductsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    vendor = UserSerializer(read_only=True)
    vendor_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Products
        fields =['id','category','category_id','name','price','description','vendor','vendor_id','fixed_price','inventory']

class UpdateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['price', 'description', 'fixed_price', 'inventory']

class AddItemToCartSerializer(serializers.ModelSerializer):
    product = CreateProductsSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    customer = UserSerializer(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Cart
        fields = ['customer', 'customer_id', 'product', 'product_id', 'quantity']

class VendorSerializedOrders(serializers.ModelSerializer):
    class Meta:
        model = VendorOrders
        fields = '__all__'

class CustomerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = '__all__'

class CustomerOffers(serializers.ModelSerializer):
    class Meta:
        model = Offers
        fields = '__all__'

class CreateCustomerOfferSerializer(serializers.ModelSerializer):
    _from_id = serializers.IntegerField(write_only=True)
    product = ProductsSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Offers
        fields = ['_from_id', 'product', 'product_id', 'offer_amount']

class VendorOffersSerializer(serializers.Serializer):
    _from_id = serializers.IntegerField()
    product_id = serializers.IntegerField()
    counter_amount = serializers.DecimalField(max_digits=8, decimal_places=2)