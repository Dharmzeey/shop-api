from django.urls import path
from . import views

app_name = "products"
urlpatterns = [
  path("categories/", views.product_categories, name="product_categories"),
  path("brands/", views.product_brands, name="product_brands"),
  
  path("", views.product_list, name="product_list"),
  path("search/", views.product_search, name="product_search"),
  path("category/<str:category_name>/", views.products_by_category, name="products_by_category"),
  path("brand/<str:category_name>/<str:brand_name>/", views.products_by_brand, name="products_by_brand"),
  path("recently-viewed/", views.recently_viewed, name="recently_viewed"),
  path("similar-products/", views.similar_products, name="similar_products"),
  path("deals/", views.deals, name="deals"),
  path("deals/<str:pk>/", views.deal_detail, name="deal_detail"),
  path("<str:pk>/", views.product_detail, name="product_detail"), 
]