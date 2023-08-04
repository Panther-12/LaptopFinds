from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('user_login/', views.user_login, name='user_login'),    
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    path('product/<int:id>', views.product, name='product'),
    path('orders/', views.orders, name='orders'),
    path('offers/', views.offers, name='offers'),
    path('cart/', views.cart, name='cart'),
    path('cart/<int:id>', views.addToCart, name='addToCart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payments/', views.mpesa_payment, name='mpesa'),
]
