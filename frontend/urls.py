from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.display_registration_form, name='register'),
    path('user_login/', views.display_login_form, name='user_login'),
    path('user_logout/', views.user_logout, name='user_logout'),    
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    path('product/<int:id>', views.product, name='product'),
    path('orders/', views.orders, name='orders'),
    path('offers/', views.offers, name='offers'),
    path('offer/<int:id>', views.send_offer, name='send_offer'),
    path('cart/', views.cart, name='cart'),
    path('cart/<int:id>', views.addToCart, name='addToCart'),
    path('create-order/', views.create_order, name='create-order'),
    path('payments/', views.mpesa_payment, name='mpesa'),
    path('add-product/<int:id>', views.add_product, name="add-product"),
    path('remove-product/<int:id>', views.remove_product, name="remove-product"),
    path('deleteCartItem/<int:id>', views.delete_cart_item, name='deleteCartItem'),
    path('cancelOrder/<int:id>', views.cancel_order, name="cancelOrder"),
]
