from django.test import TestCase
from .models import Category, Products
from django.contrib.auth.models import User

# Create your tests here.
class CategoryModelTest(TestCase):
    
    def create_category(self, title="test1"):
        return Category.objects.create(title=title)
    
    def test_create_category(self):
        category = self.create_category()
        self.assertTrue(isinstance(category, Category))
        self.assertEqual(category.title, "test1")

class ProductCreationTestCase(TestCase):
    def create_category(self, title="test2"):
        return Category.objects.create(title=title)
    def create_vendor(self, username="testuser1",email="testuser1@gmail.com",password="T3stus3r?"):
        return User.objects.create(username=username,email=email,password=password)
    def create_product(self, name="Elitebook 320g3", price=25000.00, description="An elegant piece", fixed_price=True, inventory=12):
        category = self.create_category()
        vendor = self.create_vendor()
        return Products.objects.create(name=name, category=category, vendor=vendor, price=price, description=description, fixed_price=fixed_price, inventory=inventory)
    
    def test_product_creation(self):
        product = self.create_product()
        self.assertTrue(isinstance(product, Products))
        self.assertEqual(product.name, "Elitebook 320g3")




