from django.urls import path
from . import views

app_name = "payment"
urlpatterns = [
  path("", views.initiate_payment, name="initiate_payment"),
  path("paystack/webhook/", views.paystack_webhook, name="paystack_webhook"),
]