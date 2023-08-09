from django.shortcuts import render, redirect
import requests, json
from django.contrib.auth.models import User
from .utils import send_SMS_notification
from django.http import HttpResponse
from django_daraja.mpesa.core import MpesaClient
from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm


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

def display_registration_form(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("user_login")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render (request, "register.html", context={"register_form":form})

def display_login_form(request): 
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("home")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form":form})

def user_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect("user_login")

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
    # send_SMS_notification(message=f"{product_data['name']} added to cart successfully", phone=recepients)
    return redirect(f'/site/product/{id}')

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
    print(user_cart)
    return render(request, 'cart.html', {"user_cart":user_cart})

def add_product(request, id):
    if not request.user.is_authenticated:
        return redirect("register")
    user_token = User.objects.filter(username=request.user)[0].auth_token

    # increase or decrease the quantity of the item by one
    requests.request("PUT", url=f"{base_url}/api/cart/{id}", headers={
        "Content-Type": "application/json",
        "Authorization": f"Token {user_token}"
        }, data={})

    # Fetch the current cart and display it
    user_cart = requests.request("GET", url=f"{base_url}/api/cart/", headers={
        "Content-Type": "application/json",
        "Authorization": f"Token {user_token}"
        }).json()
    return redirect("cart")

def remove_product(request, id):
    if not request.user.is_authenticated:
        return redirect("register")
    user_token = User.objects.filter(username=request.user)[0].auth_token

    # increase or decrease the quantity of the item by one
    requests.request("DELETE", url=f"{base_url}/api/cart/{id}", headers={
        "Content-Type": "application/json",
        "Authorization": f"Token {user_token}"
        }, data={})
    return redirect("cart")

def create_order(request):
    if not request.user.is_authenticated:
        return redirect("register")
    user_token = User.objects.filter(username=request.user)[0].auth_token

    # increase or decrease the quantity of the item by one
    requests.request("POST", url=f"{base_url}/api/order/", headers={
        "Content-Type": "application/json",
        "Authorization": f"Token {user_token}"
        }, data={})
    return redirect("cart")

def send_offer(request,id):
    if not request.user.is_authenticated:
        return redirect("register")
    user_id = User.objects.filter(username=request.user)[0].pk
    user_token = User.objects.filter(username=request.user)[0].auth_token
    data = {
        "_from_id":user_id,
        "product_id":id,
        "offer_amount":20000.00
    }
    # increase or decrease the quantity of the item by one
    requests.request("POST", url=f"{base_url}/api/offer/", headers={
        "Content-Type": "application/json",
        "Authorization": f"Token {user_token}"
        }, data=json.dumps(data))
    return redirect("offers")

def delete_cart_item(request,id):
    if not request.user.is_authenticated:
        return redirect("register")
    user_id = User.objects.filter(username=request.user)[0].pk
    user_token = User.objects.filter(username=request.user)[0].auth_token

    # increase or decrease the quantity of the item by one
    requests.request("DELETE", url=f"{base_url}/api/deleteCartItem/{id}", headers={
        "Content-Type": "application/json",
        "Authorization": f"Token {user_token}"
        }, data={})
    return redirect("cart")

def cancel_order(request,id):
    if not request.user.is_authenticated:
        return redirect("register")
    user_id = User.objects.filter(username=request.user)[0].pk
    user_token = User.objects.filter(username=request.user)[0].auth_token

    # increase or decrease the quantity of the item by one
    requests.request("DELETE", url=f"{base_url}/api/order/{id}", headers={
        "Content-Type": "application/json",
        "Authorization": f"Token {user_token}"
        }, data={})
    return redirect("orders")



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