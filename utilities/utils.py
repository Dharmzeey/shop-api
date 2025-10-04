from rest_framework.response import Response
from rest_framework import status

def check_lga_and_state_match(serializer):
  lga = serializer.validated_data.get("lga", None)
  state = serializer.validated_data.get("state", None)
  if state.id != lga.state.id:
    data = {"error": "The LGA passed does not belong to the state being sent"}
    return Response(data, status=status.HTTP_400_BAD_REQUEST)
  return None
