from rest_framework import serializers
from .models import State, LGA

class StateSerializer(serializers.ModelSerializer):
  class Meta:
    model = State
    fields = "__all__"

class LGASerializer(serializers.ModelSerializer):
  class Meta:
    model = LGA
    fields = "__all__"
