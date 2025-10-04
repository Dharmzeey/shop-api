from rest_framework import serializers
from base.models import State, LGA

class OrderAddressSerializer(serializers.Serializer):
    name = serializers.CharField()
    phone_number = serializers.CharField(max_length=11)
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())
    city_town = serializers.CharField(max_length=30)
    lga = serializers.PrimaryKeyRelatedField(queryset=LGA.objects.all())
    prominent_motor_park = serializers.CharField(max_length=50, required=False)
    landmark_signatory_place = serializers.CharField(max_length=50, required=False)
    address = serializers.CharField()
