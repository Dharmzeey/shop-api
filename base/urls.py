from django.urls import path
from . import views

app_name = "base"

urlpatterns = [
  path('states/', views.fetch_states, name="fetch_states"),
  path('lgas/', views.fetch_lgas, name="fetch_lgas"),
]

