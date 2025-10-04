from django.urls import path
from . import views

app_name = "users"
urlpatterns = [  
  #  user
  path('verify/', views.verify_user_info, name="verify_user_info"),
  path('info/', views.add_user_info, name="add_user_info"),
  path('info/retrieve/', views.retrieve_user_info, name="retrieve_user_info"),
  path('info/update/', views.update_user_info, name="update_user_info"),
  path('delete/', views.delete_user, name="delete_user_info"), 
  
  # address
  path('addrerss/verify/', views.verify_user_address, name="verify_user_address"),
  path('address/', views.create_user_address, name="create_user_address"),
  path('address/retrieve/', views.retrieve_user_address, name="retrieve_user_address"),
  path('address/update/', views.update_user_address, name="update_user_address"),
  
  path('orders/pending/', views.pending_orders, name="pending_orders"),
  path('orders/completed/', views.completed_orders, name="completed_orders"),
  
  path('favourites/', views.list_create_favourite, name='create_favourite_list'),
  path('favourites/<str:product_id>/', views.delete_favourite, name='delete_favourite_list'),
]
