from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import DestroyAPIView, ListAPIView, ListCreateAPIView

from authentication.permissions import IsUserVerified
from authentication.serializers import UserSerializer
from utilities.error_handler import render_errors
from utilities.utils import check_lga_and_state_match

from . import serializers as CustomSerializers
from .models import UserInfo, UserAddress, PendingOrder, CompletedOrder, Favorite


class VerifyUserInfo(APIView):
  permission_classes = [IsAuthenticated, IsUserVerified]
  def get(self, request):
    try:
      UserInfo.objects.get(user=request.user)
      return Response({"message": "User info exists"}, status=status.HTTP_200_OK)
    except UserInfo.DoesNotExist:
      return Response({"error": "User info does not exist"}, status=status.HTTP_404_NOT_FOUND)
verify_user_info = VerifyUserInfo.as_view()


class CreateUserInfoView(APIView):
  serializer_class = CustomSerializers.UserInfoSerializer
  permission_classes = [IsAuthenticated, IsUserVerified]
  
  def post(self, request):
    serializer = self.serializer_class(data=request.data)
    if not request.user.email_verified:
      return Response({"error": "Email not verified"}, status=status.HTTP_403_FORBIDDEN)
    if serializer.is_valid():
      try:
        serializer.save(user=request.user)
      except IntegrityError:
        data = {"error": "User profile already exists"}
        return Response(data, status=status.HTTP_409_CONFLICT)      
      data = {"message": "Profile created successfully", "data": serializer.data}
      return Response(data, status=status.HTTP_201_CREATED)
    data = {"errors": render_errors(serializer.errors)}
    return Response(data, status=status.HTTP_400_BAD_REQUEST)
add_user_info = CreateUserInfoView.as_view()


class RetrieveUserInfoView(APIView):
  serializer_class = CustomSerializers.UserInfoSerializer
  permission_classes = [IsAuthenticated, IsUserVerified]
  def get(self, request):
    try:
      user = request.user.user_info
    except ObjectDoesNotExist:
      data = {"message": "User is yet to fill their personal information"}
      return Response(data, status=status.HTTP_404_NOT_FOUND)    
    serializer = self.serializer_class(instance=user)
    user_serializer = UserSerializer(instance=request.user)
    data = {"message": "user details", "data": {**serializer.data, **user_serializer.data}} # returns data for user info and auth info
    return Response(data, status=status.HTTP_200_OK)
retrieve_user_info = RetrieveUserInfoView.as_view()


class UpdateUserInfoView(APIView):
  serializer_class = CustomSerializers.UserInfoSerializer
  permission_classes = [IsAuthenticated, IsUserVerified]
  
  def patch(self, request):
    try:
      UserInfo.objects.get(user=request.user)
      user = request.user.user_info
    except UserInfo.DoesNotExist:
      return Response({"error": "Add your user information"}, status=status.HTTP_404_NOT_FOUND)
    serializer = self.serializer_class(instance=user, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      data = {"message": "Profile updated successfully", "data": serializer.data}
      return Response(data, status=status.HTTP_200_OK)
    data = {"errors": render_errors(serializer.errors)}
    return Response(data, status=status.HTTP_400_BAD_REQUEST)
update_user_info = UpdateUserInfoView.as_view()


class DeleteUserView(DestroyAPIView):
  serializer_class = CustomSerializers.UserInfoSerializer
  permission_classes = [IsAuthenticated, IsUserVerified]
  def get_object(self):
    user = self.request.user
    if not user.is_authenticated:
      raise PermissionDenied("User cannot be deleted")
    return user
delete_user = DeleteUserView.as_view()


# Address

class VerifyUserAddress(APIView):
  permission_classes = [IsAuthenticated, IsUserVerified]
  def get(self, request):
    try:
      UserAddress.objects.get(user=request.user)
      return Response({"message": "User Address info exists"}, status=status.HTTP_200_OK)
    except UserInfo.DoesNotExist:
      return Response({"error": "User Address info does not exist"}, status=status.HTTP_404_NOT_FOUND)
verify_user_address = VerifyUserAddress.as_view()


class CreateUserAddressView(APIView):
  serializer_class = CustomSerializers.UserAddressSerializer
  permission_classes = [IsAuthenticated, IsUserVerified]

  def post(self, request):
    serializer = self.serializer_class(data=request.data)
    if not request.user.email_verified:
      return Response({"error": "Email not verified"}, status=status.HTTP_403_FORBIDDEN)
    if serializer.is_valid():
      validation_response = check_lga_and_state_match(serializer) 
      if validation_response:
        return validation_response
      try:
        serializer.save(user=request.user)
      except IntegrityError:
        data = {"error": "User Address profile already exists"}
        return Response(data, status=status.HTTP_409_CONFLICT)
      data = {"message": "Address created successfully", "data": serializer.data}
      return Response(data, status=status.HTTP_201_CREATED)
    data = {"errors": render_errors(serializer.errors)}
    return Response(data, status=status.HTTP_400_BAD_REQUEST)
create_user_address = CreateUserAddressView.as_view()


class RetrieveUserAddressView(APIView):
  serializer_class = CustomSerializers.UserAddressSerializer
  permission_classes = [IsAuthenticated, IsUserVerified]
  def get(self, request):
    try:
      user = request.user.user_address
    except ObjectDoesNotExist:
      data = {"message": "User is yet to fill their address information"}
      return Response(data, status=status.HTTP_404_NOT_FOUND)
    serializer = self.serializer_class(instance=user)
    data = {"message": "user address information", "data": serializer.data}
    return Response(data, status=status.HTTP_200_OK)
retrieve_user_address = RetrieveUserAddressView.as_view()


class UpdateUserAddressView(APIView):
  serializer_class = CustomSerializers.UserAddressSerializer
  permission_classes = [IsAuthenticated, IsUserVerified]
  
  def patch(self, request):
    try:
      user = UserAddress.objects.get(user=request.user)
    except UserAddress.DoesNotExist:
      return Response({"error": "Add your user Address"}, status=status.HTTP_404_NOT_FOUND)
    serializer = self.serializer_class(instance=user, data=request.data, partial=True)
    if serializer.is_valid():
      validation_response = check_lga_and_state_match(serializer)     
      if validation_response:
        return validation_response
      serializer.save()
      data = {"message": "Address updated successfully", "data": serializer.data}
      return Response(data, status=status.HTTP_200_OK)
    data = {"errors": render_errors(serializer.errors)}
    return Response(data, status=status.HTTP_400_BAD_REQUEST)
update_user_address = UpdateUserAddressView.as_view()


class PendingOrdersView(ListAPIView):
  serializer_class = CustomSerializers.PendingOrderSerializer
  permission_classes = [IsAuthenticated, IsUserVerified]
  
  def get_queryset(self):
    qs = PendingOrder.objects.filter(user=self.request.user.id)
    return qs
pending_orders = PendingOrdersView.as_view()


class CompletedOrdersView(ListAPIView):
  serializer_class = CustomSerializers.CompletedOrderSerializer
  permission_classes = [IsAuthenticated, IsUserVerified]
  
  def get_queryset(self):
    qs = CompletedOrder.objects.filter(user=self.request.user.id)
    return qs
completed_orders = CompletedOrdersView.as_view()


class FavoriteListCreateView(ListCreateAPIView):
    serializer_class = CustomSerializers.FavoriteSerializer
    permission_classes = [IsAuthenticated, IsUserVerified]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
list_create_favourite = FavoriteListCreateView.as_view()


class FavoriteDeleteView(DestroyAPIView):
    serializer_class = CustomSerializers.FavoriteSerializer
    permission_classes = [IsAuthenticated, IsUserVerified]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        product_uuid = self.kwargs.get('product_id')
        
        favorite = self.get_queryset().filter(product__uuid=product_uuid).first()
        if favorite:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Favorite not found"}, status=status.HTTP_404_NOT_FOUND)
delete_favourite = FavoriteDeleteView.as_view()
