from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, ListAPIView
from . import serializers as customSerializers
from .models import Product, Category, Brand, Deal
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from utilities.custom_authentication import CustomJWTAuthentication


class ProductCategoryView(ListAPIView):
  serializer_class = customSerializers.CategorySerializer
  queryset = Category.objects.all()
  
product_categories = ProductCategoryView.as_view()


class ProductBrandView(ListAPIView):
  """ 
  This list all the brands, of a particular category
  E.g when phone is passed, it shows return Iphone, samsung etc
  """
  serializer_class = customSerializers.BrandSerializer
  
  def get_queryset(self):
    q = self.request.query_params.get("q")
    qs = Brand.objects.filter(category__name__iexact=q)
    return qs
  
product_brands = ProductBrandView.as_view()


class ProductListView(ListAPIView):
  serializer_class = customSerializers.ProductSerializer
  queryset = Product.objects.all()
  
product_list = ProductListView.as_view()


class ProductSearchView(ListAPIView):
	serializer_class = customSerializers.ProductSerializer

	def get_queryset(self):
		q = self.request.query_params.get("q")
		qs = Product.objects.filter(name__icontains=q)
		return qs
  
product_search = ProductSearchView.as_view()


class ProductsByCategoryView(ListAPIView):
	serializer_class = customSerializers.ProductSerializer

	def get_queryset(self):
		category_name = self.kwargs.get("category_name")
		return Product.objects.filter(category__name__iexact=category_name)

products_by_category = ProductsByCategoryView.as_view()


class ProductByBrand(ListAPIView):
	serializer_class = customSerializers.ProductSerializer

	def get_queryset(self):
		category_name = self.kwargs.get("category_name")
		brand_name = self.kwargs.get("brand_name")
		return Product.objects.filter(category__name__iexact=category_name, brand__name__iexact=brand_name)
products_by_brand = ProductByBrand.as_view()


class RecentlyViewedView(ListAPIView):
	serializer_class = customSerializers.ProductSerializer
	def get_queryset(self):
		q_list = self.request.query_params.getlist("q_list[]")
		if q_list:
			try:
				qs = Product.objects.filter(uuid__in=q_list)
			except ValidationError: 
				qs = Product.objects.none()
		else:
			qs = Product.objects.none()
		return qs
recently_viewed = RecentlyViewedView.as_view()


class SimilarProductsView(ListAPIView):
    serializer_class = customSerializers.ProductSerializer
    def get_queryset(self):
        product_uuid = self.request.query_params.get("product_id")
        if product_uuid:
            try:
                product = Product.objects.get(uuid=product_uuid)
                similar_products = Product.objects.filter(brand=product.brand).order_by("?")[:7]
            except (Product.DoesNotExist, ValidationError):
                similar_products = Product.objects.none()
        else:
            similar_products = Product.objects.none()
        return similar_products
similar_products = SimilarProductsView.as_view()


class ProductDetailView(RetrieveAPIView):
	queryset=Product.objects.all()
	permission_classes = [AllowAny]
	authentication_classes = [CustomJWTAuthentication]
	serializer_class = customSerializers.ProductSerializer
	def get_object(self):
		uuid = self.kwargs.get('pk')
		try:
			return Product.objects.get(uuid=uuid)
		except (Product.DoesNotExist, ValidationError):
			raise Http404
product_detail = ProductDetailView.as_view()


class DealListView(ListAPIView):
	serializer_class = customSerializers.DealSerializer
	queryset = Deal.objects.all()
deals = DealListView.as_view()


class DealDetailView(RetrieveAPIView):
	serializer_class = customSerializers.DealSerializer
	queryset=Deal.objects.all()
	def get_object(self):
		uuid = self.kwargs.get('pk')
		try:
			return Deal.objects.get(uuid=uuid)
		except (Deal.DoesNotExist, ValidationError):
			raise Http404
deal_detail = DealDetailView.as_view()