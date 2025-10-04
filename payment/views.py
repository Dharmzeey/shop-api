import hmac
import hashlib
import json
import base64
import pickle
from datetime import timedelta
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from authentication.permissions import IsUserVerified
from base.models import State, LGA 
from cart.service import Cart
from products.models import Product
from users.models import PendingOrder

from .models import Payment
from. paystack import Paystack


class InitiatePayment(APIView):
    permission_classes = [IsAuthenticated, IsUserVerified]
    def post(self, request):
        cart = Cart(request)
        payment = Paystack()
        # session
        get_session_id = request.session.session_key
        session_obj = Session.objects.get(session_key=get_session_id)
        session_data = session_obj.get_decoded()
        encoded_session_data = base64.b64encode(pickle.dumps(session_data)).decode()
        if not (cart.address and cart.cart):
            """
            This means if the user still wants to access payment modal and cart is empty
            """
            data = {"error": "No item in cart"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        delivery_fee = cart.address['delivery_fee']    
        payment_init = payment.initialize_payment(email=request.user.email, amount=cart.get_total_price() + delivery_fee)
        # access code is returned to FE to resume and continue tnx
        if payment_init[0] == 200: # if the first item in the tuple which is the status code
            payment = Payment.objects.create(user=request.user, amount=cart.get_total_price() + delivery_fee, email=request.user.email, access_code=payment_init[1], ref=payment_init[2], session_id=request.session.session_key, session_data=encoded_session_data)
            payment.save()
            data = {"access_code": payment_init[1]}
            # access code is returned to FE to resume and continue tnx
            return Response(data, status=status.HTTP_200_OK)
        elif payment_init[0] == 500:
            data = {"error": "payment initialization timed out"}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            data = {"error": "payment could not be initialized"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
initiate_payment = InitiatePayment.as_view()


class PaystackWebhookView(APIView):
    def post(self, request):
        secret = settings.PAYSTACK_SECRET_KEY
        payload = request.body
        hash = hmac.new(
            key=secret.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha512
        ).hexdigest()
        if hash != request.headers.get("x-paystack-signature"):
            return JsonResponse({"status": "invalid signature"}, status=400)
        else:
            data = json.loads(payload)
            if (data['event'] == 'charge.success'):
                user_email = data['data']['customer']['email']
                transaction_id = data['data']['id']
                reference_id = data['data']['reference']
                amount = int(data['data']['amount']) / 100 # return back to NGN from kobo
                if check_payment(reference_id):
                    process_order(reference_id, amount, user_email)   
            return JsonResponse({"status": "success"}, status=200)
paystack_webhook = PaystackWebhookView.as_view()


def check_payment(reference):
    paystack = Paystack()
    payment_status = paystack.verify_payment(reference)
    if payment_status[0] == True:
        return True
    return False
    

def process_order(reference, amount, user_email):
    user = User.objects.get(email=user_email)
    get_payment = Payment.objects.get(ref=reference, amount=amount)
    get_payment.verify_payment() # change the verified status of the model to True
    get_payment.save()
    decoded_session_data = pickle.loads(base64.b64decode(get_payment.session_data.encode()))
    session_cart = decoded_session_data.get(settings.CART_SESSION_ID)
    session_address = decoded_session_data.get(settings.ADDRESS_SESSION_ID)
    for item_id, item_data in session_cart.items():
        # product
        product = Product.objects.get(uuid=item_id)
        price=product.price
        quantity = item_data.get('quantity')
        product_name = product.name
        # address        
        name = session_address['address_info'].get('name')
        phone_number = session_address['address_info'].get('phone_number')
        state = State.objects.get(id=session_address['address_info'].get('state'))
        city_town = session_address['address_info'].get('city_town')
        lga = LGA.objects.get(id=session_address['address_info'].get('lga'))
        prominent_motor_park = session_address['address_info'].get('prominent_motor_park')
        landmark_signatory_place = session_address['address_info'].get('landmark_signatory_place')
        address = session_address['address_info'].get('address')
        delivery_days = lga.delivery_days
        order = PendingOrder.objects.create(
            user=user,
            name=name,
            phone_number=phone_number,
            state=state,
            city_town=city_town,
            lga=lga,
            prominent_motor_park=prominent_motor_park,
            landmark_signatory_place=landmark_signatory_place,
            address=address,
            # product info
            product=product,
            price=price,
            quantity=quantity,
            product_name=product_name,
            estimated_delivery_date=timezone.now() + timedelta(days=delivery_days)
        )
        order.save()
         # Remove cart data from the session current and save it
        session_obj = Session.objects.get(session_key=get_payment.session_id)
        session_data = session_obj.get_decoded()
        session_data.pop(settings.CART_SESSION_ID, None)  # Remove cart data safely
        session_data.pop(settings.ADDRESS_SESSION_ID, None)  # Remove cart data safely
        session_obj.session_data = session_data  # Update the session object
        session_obj.save()  # Save the session

    # after the order is being processed, cart and address are removed from the session and the quantity of product is decreased by number purchased
