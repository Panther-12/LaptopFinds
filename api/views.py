from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework import status
from .models import Category, Products, Orders, Offers, VendorOrders, Cart
from .serializers import CategorySerializer, ProductsSerializer, UpdateProductSerializer, AddItemToCartSerializer, VendorSerializedOrders, CustomerOrderSerializer, CustomerOffers, CreateProductsSerializer, CreateCustomerOfferSerializer 
from .serializers import VendorOffersSerializer
from .utils import calculate_cart_total, last_item, paginate_items
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
# from requests import post, put, get

# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def category(request):
    if request.method == 'POST':
        isAdmin = User.objects.filter(is_superuser=True)
        if isAdmin:
            serialized_data = CategorySerializer(data=request.data)
            if serialized_data.is_valid():
                serialized_data.save()
                return Response(serialized_data.validated_data, status.HTTP_201_CREATED)
            return Response({"message":"Invalid data provided"}, status.HTTP_400_BAD_REQUEST)
        return Response({"message":"Only admins allowed"},status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        categories = Category.objects.all()
        serialized_data = CategorySerializer(categories, many=True)
        return Response(serialized_data.data, status.HTTP_200_OK)
    return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@csrf_exempt
def product(request):
    if request.method == 'GET':
        if request.user.groups.filter(name="customers") or request.user.groups.filter(name="admins") or request.user.groups.filter(name=""):
            products = Products.objects.select_related('category').all()
            products = paginate_items(request, products)
            serialized_data = ProductsSerializer(products, many=True)
            return Response(serialized_data.data, status.HTTP_200_OK)
        
        user = User.objects.filter(username=request.user)[0].pk
        products = Products.objects.filter(vendor=user)
        products = paginate_items(request, products)
        serialized_data = ProductsSerializer(products, many=True)
        return Response(serialized_data.data, status.HTTP_200_OK)
    
    if request.method == 'POST':
        if request.user.groups.filter(name="vendors") or request.user.groups.filter(name="admins"):
            product = CreateProductsSerializer(data=request.data)
            if product.is_valid():
                product.save()
                return Response({"message":"Product created successfully"}, status.HTTP_201_CREATED)
            return Response({"message":"Invalid product data"}, status.HTTP_400_BAD_REQUEST)
        return Response({"message":"Only vendors and admins"}, status.HTTP_401_UNAUTHORIZED)
    return Response(status.HTTP_400_BAD_REQUEST)  


@api_view(['GET','PUT'])
@csrf_exempt
def singleProduct(request, id):
    try:
        product = Products.objects.get(pk=id)
    except product.DoesNotExist:
        return Response(status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serialized_product = CreateProductsSerializer(product)
        return Response(serialized_product.data, status.HTTP_200_OK)
    
    if request.method == 'PUT':
        if len(request.user.groups.filter(name="vendors"))<=0 and len(request.user.groups.filter(name="admins"))<=0:
            return Response({"message":"Only vendors and admins"}, status.HTTP_401_UNAUTHORIZED)
        
        serialized_product = UpdateProductSerializer(product, data=request.data)
        if serialized_product.is_valid():
            serialized_product.save()
            return Response({"message":"Product added successfully"}, status.HTTP_200_OK)
        return Response({"message":"Invalid product data"}, status.HTTP_400_BAD_REQUEST)
    return Response(status.HTTP_400_BAD_REQUEST)
        
@api_view(['POST','GET'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def cart(request):
    if request.user.groups.filter(name="customers") or request.user.groups.filter(name="admins"):
        if request.method == 'POST':
                cart_item = AddItemToCartSerializer(data=request.data)
                if cart_item.is_valid():
                    # check whether item already exists in cart
                    # product_id = cart_item.data.get('product_id')
                    # cart = Cart.objects.all()
                    # for item in cart:
                    #     if item.product.pk == product_id:
                    #         return Response({"message":"item already exists in cart"}, status.HTTP_200_OK)
                    cart_item.save()
                    cart = Cart.objects.all()
                    for item in cart:
                        item.amount = item.product.price
                        item.save(update_fields=['amount'])
                    return Response({"message":"Product added successfully"}, status.HTTP_201_CREATED)
                return Response({"message":"Invalid product data"}, status.HTTP_400_BAD_REQUEST)
        
        if request.method == 'GET':
            user_id = User.objects.get(username=request.user).pk
            if user_id is not None:
                new_cart = Cart()
                user_cart = new_cart.generateCart(customerId=user_id)
                if not isinstance(user_cart, list):
                    return Response({"message":user_cart}, status.HTTP_204_NO_CONTENT)
                # Check if there is an accepted offer update from the customer
                total = calculate_cart_total(user_cart)
                order_sum=0
                for item in user_cart:
                    order_sum+=item['quantity']
                return Response({"total": total,"cart":user_cart, "items":order_sum}, status.HTTP_200_OK)
            return Response({"message":"User does not exist"}, status.HTTP_204_NO_CONTENT)
    return Response({"message":"Create a customer account to proceed"}, status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT', 'DELETE'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def updateQuantity(request, id):
    try:
        cart_item = Cart.objects.get(pk=id)
    except cart_item.DoesNotExist:
        return Response({"message":"cart item does not exist"}, status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        if request.user.groups.filter(name="customers") or request.user.groups.filter(name="admins"):
            # update the quantity
            cart_item.quantity+=1
            cart_item.product.inventory-=1
            cart_item.amount=cart_item.product.price*cart_item.quantity
            cart_item.save(update_fields=['quantity', 'amount','product'])
            return Response({"message":"Product added successfully"}, status.HTTP_200_OK)
        return Response({"message":"only customers and admins allowed"}, status.HTTP_403_FORBIDDEN)
    if request.method == 'DELETE':
        if request.user.groups.filter(name="customers") or request.user.groups.filter(name="admins"):
            # update the quantity
            if cart_item.quantity >1:
                cart_item.quantity-=1
            cart_item.product.inventory+=1
            cart_item.amount=cart_item.product.price*cart_item.quantity
            cart_item.save(update_fields=['quantity', 'amount','product'])
            return Response({"message":"Product removed successfully"}, status.HTTP_200_OK)
        return Response({"message":"only customers and admins allowed"}, status.HTTP_403_FORBIDDEN)
    return Response(status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def deleteCartItem(request, id):
    try:
        cart_item = Cart.objects.get(pk=id)
    except cart_item.DoesNotExist:
        return Response({"message":"cart item does not exist"}, status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        if request.user.groups.filter(name="customers") or request.user.groups.filter(name="admins"):
            cart_item.delete()
            return Response({"message":"Product deleted successfully"}, status.HTTP_200_OK)
        return Response({"message":"only customers and admins allowed"}, status.HTTP_403_FORBIDDEN)
    return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['GET','POST'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def order(request):
    if request.user.groups.filter(name="vendors"):
        if request.method == 'GET':
            vendor_id = User.objects.filter(username=request.user)[0].pk
            vendor_orders = VendorOrders.objects.filter(vendor=vendor_id)
            if len(vendor_orders) >=1:
                vendor_orders = paginate_items(request, vendor_orders)
                serialized_orders = VendorSerializedOrders(vendor_orders, many=True)
                return Response(serialized_orders.data, status.HTTP_200_OK)
            return Response({"message":"No orders exist"}, status.HTTP_204_NO_CONTENT)
        return Response(status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        # use the customer orders model serilizer
        user_id = User.objects.filter(username=request.user)[0].pk
        if request.user.groups.filter(name="customers") or request.user.groups.filter(name="admins"):
            order_items = Orders.objects.filter(customer=user_id)
            order_items = paginate_items(request, order_items)
            serialized_orders = CustomerOrderSerializer(order_items, many=True)
            return Response(serialized_orders.data, status.HTTP_200_OK)
        return Response({"message": "unauthorized user"}, status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        # Generate cart
        user = User.objects.filter(username=request.user)[0]
        cart_products = Cart()
        get_cart = cart_products.generateCart(user.pk)
        products = ''
        user_offers = Offers.objects.filter(_from_id=user.pk)
        if(len(user_offers)>0):
            for item in get_cart:
                products += f"{item['product_name']:item['price']:item['vendor_name']},"
            # Check for any accepted offers for this product from customer
            # Get offer amounts from the user for each and every product in the list
                for offer in user_offers:
                    if offer.state == True:
                        if offer.product.pk == item['product_id']:
                            if offer.counter_amount == 0.0:
                                item['price'] = offer.offer_amount
                            item['price'] = offer.counter_amount
                vendor_order = VendorOrders(vendor_id=item['vendor_id'], product_name=item['product_name'], product_price=item['price'], quantity=item['quantity'], customer_name=user.username, customer_phone=user.last_name)
                vendor_order.save()
        total = calculate_cart_total(get_cart)
        customer_order = Orders(customer_id=user.id, products=products, total=total, status=False, date=now())
        customer_order = customer_order.save()
        # use customer orders model serializer
        return Response(customer_order, status.HTTP_201_CREATED)

@api_view(['PUT','DELETE'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def singleOrder(request, id):
    if request.method == 'PUT':
        if request.user.groups.filter(name="customers"):
            order = Orders.objects.get(pk=id)
            order.status = True
            order.save(update_fields=['status'])
            for item in order.products.split(','):
                vendor_name = item.split(':')[2]
                vendor_id = User.objects.filter(username=vendor_name)[0]
                product_name = item.split(':')[0]

                vendor_order = VendorOrders.objects.filter(vendor_id=vendor_id)
                product = vendor_order.filter(product_name=product_name)[0]

                product.paid_status = True
                product.delivery_status = True
                product.save(update_fields=['paid_status', 'delivery_status'])
            return Response("Order delivered successfully", status.HTTP_200_OK)
                
    if request.method == 'DELETE':
        order = Orders.objects.get(pk=id)
        order.cancelled_status = True
        order.save(update_fields=['cancelled_status'])
        for item in order.products.split(','):
            vendor_name = item.split(':')[2]
            vendor_id = User.objects.filter(username=vendor_name)[0]
            product_name = item.split(':')[0]

            vendor_order = VendorOrders.objects.filter(vendor_id=vendor_id)
            product = vendor_order.filter(product_name=product_name)[0]

            product.cancelled_status = True
            product.save(update_fields=['cancelled_status'])
        return Response({"message": "Order cancelled successfully"}, status.HTTP_200_OK)
    return Response({}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET','POST'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def offer(request):
    user = User.objects.filter(username=request.user)[0]
    if request.method == 'POST':
        if request.user.groups.filter(name="customers") or request.user.groups.filter(name="admins"):
            serialized_offer = CreateCustomerOfferSerializer(data=request.data)
            if serialized_offer.is_valid():
                serialized_offer.save()
                return Response(serialized_offer.validated_data, status.HTTP_201_CREATED)
            return({"message": "invalid data provied"}, status.HTTP_400_BAD_REQUEST)
        if request.user.groups.filter(name="vendors"):
            serialized_vendor_offer = VendorOffersSerializer(data=request.data)
            if serialized_vendor_offer.is_valid():    
                customer_offer = Offers.objects.filter(_from_id=serialized_vendor_offer.data.get('_from_id'))
                product = customer_offer.filter(product_id=serialized_vendor_offer.data.get('product_id'))
                last_product = last_item(product)
                vendor = Products.objects.filter(pk=last_product.product.pk)[0].vendor
                vendor_name = vendor.username
                current_user = User.objects.filter(username=request.user)[0].username
                    
                if vendor_name == current_user:
                    last_product.counter_amount = serialized_vendor_offer.data.get('counter_amount')
                    last_product.save(update_fields=['counter_amount'])
                    return Response({"message": "counter offer sent successfully"}, status.HTTP_200_OK)
                return Response({"message": "This product does not belong to you"}, status.HTTP_400_BAD_REQUEST)
            return Response({"message": "invalid data"}, status.HTTP_400_BAD_REQUEST)
        return Response({}, status.HTTP_401_UNAUTHORIZED)
        
    if request.method == 'GET':
        if request.user.groups.filter(name="vendors"):
            vendor_offers = []
            offers = Offers.objects.all()
            for offer in offers:
                if offer.product.vendor.pk == user.id:
                    vendor_offers.append({"customer_id":offer._from.pk, "customer_name":offer._from.username, "product_id":offer.product.pk, "product_name":offer.product.name, "offer_amount":offer.offer_amount, "counter_amount":offer.counter_amount})
            return Response(vendor_offers, status.HTTP_200_OK)
        if request.user.groups.filter(name="customers") or request.user.groups.filter(name="admins"):
            offers = Offers.objects.filter(_from_id=user.pk)
            offers = paginate_items(request, offers)
            serialized_offers = CustomerOffers(offers, many=True)
            return Response(serialized_offers.data, status.HTTP_200_OK)
    return Response({}, status.HTTP_403_FORBIDDEN)


@api_view(['GET','PUT','DELETE'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def singleOffer(request, id):
    user = User.objects.filter(username=request.user)[0]
    try:
        offer = Offers.objects.get(pk=id)
    except Offers.DoesNotExist:
        return Response({}, status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        if request.user.groups.filter(name="customers") or request.user.groups.filter(name="admins"):
            if offer._from_id == user.pk:
                serialized_offers = CustomerOffers(offer)
                return Response(serialized_offers.data, status.HTTP_200_OK)
            return Response({"message": "This product does not belong to you"}, status.HTTP_400_BAD_REQUEST)
        if request.user.groups.filter(name="vendors"):
            if offer.product.vendor.pk == user.id:
                serialized_offers = CustomerOffers(offer)
                return Response(serialized_offers.data, status.HTTP_200_OK)
            return Response({"message": "This product does not belong to you"}, status.HTTP_400_BAD_REQUEST)
        
    if request.method == 'PUT':
        if request.user.groups.filter(name="vendors"):
            if offer.product.vendor.pk == user.id:
                offer.state = True
                offer.save(update_fields=['state'])
                return Response({"message": "Offer accepted"}, status.HTTP_200_OK)
            return Response({"message": "This product does not belong to you"}, status.HTTP_400_BAD_REQUEST)
        if request.user.groups.filter(name="customers") or request.user.groups.filter(name="admins"):
            if offer._from_id == user.pk:
                offer.state = True
                offer.save(update_fields=['state'])
                return Response({"message": "Offer accepted"}, status.HTTP_200_OK)
            return Response({"message": "This product does not belong to you"}, status.HTTP_400_BAD_REQUEST)
        return Response({"message":"not allowed"}, status.HTTP_403_FORBIDDEN)
    
    if request.method == "DELETE":
        if request.user.groups.filter(name="customers"):
            offer.delete()
            return Response({"message":"offer deleted"}, status.HTTP_200_OK)
        return Response({}, status.HTTP_403_FORBIDDEN)
    return Response({}, status.HTTP_400_BAD_REQUEST)
        
    
            



