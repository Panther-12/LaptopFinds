from django.shortcuts import render, redirect
import requests, json
from django.contrib.auth.models import User
from .utils import send_SMS_notification
from django.http import HttpResponse
from django_daraja.mpesa.core import MpesaClient


# TODO
# Finish product page design
# Update the product model to include specification field: weight,sku and model.
# Update the user model to include location for vendors
# 1. Design cart page
# 2. Create order functionality
# 3. Checkout functionality
# 4. Login, registrations and logout functionality

base_url = "http://localhost:8000"
# Create your views here.
def home(request):
    return render(request, 'index.html', {})

def register(request):
    return render(request, 'register.html', {})

def user_login(request):
    return render(request, 'login.html', {})

def user_logout(request):
    logout = requests.request("POST", url=f"{base_url}/auth/token/logout", data={})
    return render(request, 'login.html', {})

def about(request):
    return render(request, 'about.html', {})

def product(request, id):
    # This is where the add to cart button is located
    # On clicking this button the product is added to cart and the "add to cart button"
    # is replaced by add/remove to inventory component
    # On click add a loading icon takes the place of the input field and the product quantity in the cart is increased while the quantity in the product model is decreased
    product_data = requests.request("GET", url=f"{base_url}/api/product/{id}", headers={"Content-Type": "application/json"}).json()
    return render(request, 'product.html', {"product":product_data, "message":""})

def addToCart(request, id):
    if not request.user.is_authenticated:
        return redirect("register")
    user_id = User.objects.filter(username=request.user)[0].pk
    user_token = User.objects.filter(username=request.user)[0].auth_token
    old_phone = User.objects.filter(username=request.user)[0].last_name

    phone_number = "+254"+old_phone[1:]
    recepients = []
    recepients.append(phone_number)


    user_data = {
            "customer_id": user_id,
            "product_id": id,
            "quantity":1
        }
    add_to_cart = requests.request("POST", url=f"{base_url}/api/cart/", headers={
        "Content-Type": "application/json",
        "Authorization": f"Token {user_token}"
        }, data=json.dumps(user_data)
        ).json()
    product_data = requests.request("GET", url=f"{base_url}/api/product/{id}", headers={"Content-Type": "application/json"}).json()
    send_SMS_notification(message=f"{product_data['name']} added to cart successfully", phone=recepients)
    return render(request, 'product.html', {"product":product_data, "message":add_to_cart})

def products(request):
    return render(request, 'products.html')

def offers(request):
    if not request.user.is_authenticated:
        return redirect("register")
    return render(request, 'offers.html', {})

def orders(request):
    if not request.user.is_authenticated:
        return redirect("register")
    return render(request, 'orders.html', {})

def cart(request):
    if not request.user.is_authenticated:
        return redirect("register")
    user_token = User.objects.filter(username=request.user)[0].auth_token
    user_cart = requests.request("GET", url=f"{base_url}/api/cart/", headers={
        "Content-Type": "application/json",
        "Authorization": f"Token {user_token}"
        }).json()
    return render(request, 'cart.html', {"user_cart":user_cart})


def checkout(request):
    return render(request, 'orders.html', {})


def mpesa_payment(request):
    cl = MpesaClient()
    # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
    phone_number = '0740837666'
    amount = 1
    account_reference = 'reference'
    transaction_desc = 'Laptop finds order 1 payment'
    callback_url = 'https://api.darajambili.com/express-payment'
    response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
    return HttpResponse(response)