from django.urls import path
from . import views


urlpatterns = [
        path('category/', views.category, name='category'),
        path('product/', views.product, name='product'),
        path('product/<int:id>', views.singleProduct, name='single-product'),
        path('order/', views.order, name='order'),
        path('order/<int:id>', views.singleOrder, name='single-order'),
        path('offer/', views.offer, name='offer'),
        path('offer/<int:id>', views.singleOffer, name='single-offer'),
        path('cart/', views.cart, name='cart'),
]
