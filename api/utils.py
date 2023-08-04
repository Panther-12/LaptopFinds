# import package
import africastalking # issue: not recognized when installed in a virtual environment
                      # only when in global installation
from django.core.paginator import Paginator, EmptyPage

def calculate_cart_total(cart):
    sum=0
    for item in cart:
        sum+=item['price']
    return sum


def send_SMS_notification(message, phone):
    # Initialize SDK
    username = "YOUR_USERNAME"    # use 'sandbox' for development in the test environment
    api_key = "YOUR_API_KEY"      # use your sandbox app API key for development in the test environment
    africastalking.initialize(username, api_key)


    # Initialize a service e.g. SMS
    sms = africastalking.SMS


    # Use the service synchronously
    response = sms.send(message, phone)
    return "Message sent successfully"

# Quick sort
def sort_products(products):
    pass

# Binary search
def search_for_products(products, find):
    pass

def order_products(products):
    pass

def last_item(array):
    last_item = None
    for item in enumerate(array):
        if item[0] == len(array) - 1:
            last_item = item[1]
    return last_item

def paginate_items(request,items):
    # pagination
    perpage = request.query_params.get('perpage', default=8)
    page = request.query_params.get('page', default=1)

    paginator = Paginator(items, perpage)
    try:
        items = paginator.page(number=page)
    except EmptyPage:
        items = []
    return items