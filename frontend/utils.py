import africastalking

def send_SMS_notification(message, phone):
    # Initialize SDK
    username = "KemTest"    # use 'sandbox' for development in the test environment
    api_key = "90f05117fadbd742adba0eadf46d8f27f8bd6e95c8b68f57100a08e3fc197a7c"      # use your sandbox app API key for development in the test environment
    africastalking.initialize(username, api_key)


    # Initialize a service e.g. SMS
    sms = africastalking.SMS


    # Use the service synchronously
    sms.send(message, phone)
    return "Message sent successfully"