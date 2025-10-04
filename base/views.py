from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers as CustomSerializers
from .models import State, LGA

CACHE_TIMEOUT = 3600 * 24

class FetchStatesView(APIView):
    def get(self, request):
        
        cache_key = "all_states"
        states_data = cache.get(cache_key)
        if not states_data:
            states = State.objects.all()
            state_serializer = CustomSerializers.StateSerializer(instance=states, many=True)    
            states_data = {
                "states": state_serializer.data,
            }
            cache.set(cache_key, states_data, CACHE_TIMEOUT)
        
        return Response(states_data, status=status.HTTP_200_OK)

fetch_states = FetchStatesView.as_view()


class FetchLGAView(APIView):
    def get(self, request):
        
        state_id = request.query_params.get("state_id")        
        cache_key = f"lgas_{state_id}"        
        lgas_data = cache.get(cache_key)
        
        if not lgas_data:
            lgas = LGA.objects.filter(state__id=state_id)
            lga_serializer = CustomSerializers.LGASerializer(instance=lgas, many=True)    
            lgas_data = {
                "lgas": lga_serializer.data,
            }
            cache.set(cache_key, lgas_data, CACHE_TIMEOUT)
        
        return Response(lgas_data, status=status.HTTP_200_OK)

fetch_lgas = FetchLGAView.as_view()
