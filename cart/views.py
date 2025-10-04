from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from authentication.permissions import IsUserVerified
from utilities.error_handler import render_errors
from utilities.utils import check_lga_and_state_match

from authentication.serializers import UserSerializer
from users.serializers import UserInfoSerializer, UserAddressSerializer

from .service import Cart
from .serializers import OrderAddressSerializer


class GetCartView(APIView):
    
    def get(self, request, format=None):
        cart = Cart(request)
        return Response(
            {   
                "data": list(cart.__iter__(request)),
                "item_count": cart.__len__(),
                "grand_total_price": cart.get_total_price()                
            },
            status=status.HTTP_200_OK
            )
get_cart = GetCartView.as_view()


class ModifyCartView(APIView):
    """
    API to handle update, reduce, delete cart operations
    """

    def post(self, request, **kwargs):
        product_uuid = request.data["product_id"]
        action = request.data.get("action")
        cart = Cart(request)
        action_status = False
        
        # action status is either Trur or false returned by the service.py when an action succeeds or not
        if action == "increament":
            action_status = cart.increament(product_uuid=product_uuid)
        
        elif action == "decreament":
            action_status = cart.decreament(product_uuid=product_uuid)
            
        elif action == "update":
            quantity = request.data.get("quantity", 0)
            action_status = cart.update(product_uuid=product_uuid, quantity=quantity)
            
        elif action == "remove":
            action_status = cart.remove(product_uuid=product_uuid)
            
        elif action == "clear":
            action_status = cart.clear()
            
        else:
            return Response(
                {"error": "Action not recognized"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # if action_status returns true
        if action_status:
            return Response(
            {"message": "cart updated"},
            status=status.HTTP_202_ACCEPTED
        )
        else:
            return Response(
            {"error": "Product not found"},
            status=status.HTTP_404_NOT_FOUND
            )
    
        
modify_cart = ModifyCartView.as_view()


def _get_cart_summary(cart, request):
    cart_list = list(cart.__iter__(request=request))
    grand_total = cart.get_total_price()
    data = {}
    data_list = []
    for i in cart_list:
        data_list.append(
            {
                "cart_item_id": i['product']['id'],
                "cart_item_name": i['product']['name'],
                "cart_item_quantity": i['quantity'],
                "cart_item_price": i['price'] * i['quantity'],
            }
        )
    data.update(
        {
            "item_list": data_list,
            "grand_total": grand_total
        }
    )    
    return data


class UserCheckoutDetails(APIView):
    permission_classes = [IsAuthenticated, IsUserVerified]
    def get(self, request):
        try:
            user = request.user
            user_info = request.user.user_info
            user_address = request.user.user_address
            user_serializer = UserSerializer(instance=user)
            user_info_serializer = UserInfoSerializer(instance=user_info)
            user_address_serializer = UserAddressSerializer(instance=user_address)
            data = {
                'name': f'{user_info_serializer.data["first_name"]} {user_info_serializer.data["last_name"]}',
                'place': f'{user_address_serializer.data["city_town"]}, {user_address_serializer.data["state_name"]}',
                'address': f'{user_address_serializer.data["address"]}',
                'phone_number': f'{user_serializer.data["phone_number"]}',
                'alternative_phone_number': f'{user_info_serializer.data["alternative_phone_number"]}',
                'delivery_fee': str(user_address.lga.delivery_fee),
                'delivery_days': str(user_address.lga.delivery_days)
            }
            data = {"message": "user checkout information", "data": data}
            return Response(data, status=status.HTTP_200_OK)
        except:
            return Response({"error": "An error occured"}, status=status.HTTP_404_NOT_FOUND)
user_checkout_details = UserCheckoutDetails.as_view()


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated, IsUserVerified]
    def get(self, request):
        cart = Cart(request)
        data = _get_cart_summary(cart, request)    
        return Response(data, status=status.HTTP_200_OK)
checkout = CheckoutView.as_view()


class OrderSummary(APIView):
    permission_classes = [IsAuthenticated, IsUserVerified]
    serializer_class = OrderAddressSerializer
    def post(self, request):
        cart = Cart(request)
        serializer = self.serializer_class(data=request.data)
        use_default = request.data.get("use_default", False)
        if use_default:
            try:                    
                user_phone = request.user.phone_number
                user_info = request.user.user_info
                user_address = request.user.user_address
                address_info = cart.include_address(
                    True,
                    user_phone=user_phone,
                    user_info=user_info,
                    user_address=user_address
                )
                data = {
                    "cart_summary": _get_cart_summary(cart, request),
                    "address_info": address_info
                }
                return Response(data, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                data = {
                    "message": "User should fill their user and address information"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        if serializer.is_valid():
            validated_response = check_lga_and_state_match(serializer)
            if validated_response:
                return validated_response
            address_info = cart.include_address(False, serializer=serializer.data)
            data = {
                "cart_summary": _get_cart_summary(cart, request),
                "address_info": address_info
            }
            return Response(data, status=status.HTTP_200_OK)
        data = {
            "error": render_errors(serializer.errors)
        }
        print(serializer.errors)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
order_summary = OrderSummary.as_view()
