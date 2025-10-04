from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer

from .models import UserInfo, UserAddress, PendingOrder, CompletedOrder, Favorite

  
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ["first_name", "last_name", "other_name", "alternative_email", "alternative_phone_number"]


class UserAddressSerializer(serializers.ModelSerializer):
    state_name = serializers.SerializerMethodField()
    lga_name = serializers.SerializerMethodField()
    class Meta:
        model = UserAddress
        fields = ["state", "state_name", "city_town", "lga", "lga_name","prominent_motor_park", "landmark_signatory_place", "address"]
        extra_kwargs = {
        "state": {"required": True},
        "city_town": {"required": True},
        "lga": {"required": True},
        "address": {"required": True},
      }
    # the names are included because of when the user details is sent just for viewing, it originally shows the id, and id is very needed for creation and editing, so hence the initially field and the field_name
    def get_state_name(self, obj):
        if obj.state:
            return obj.state.name
        return None

    def get_lga_name(self, obj):
        if obj.lga:
            return obj.lga.name
        return None
    

class PendingOrderSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()
    estimated_delivery_date = serializers.DateTimeField(format="%Y-%m-%d ")
    class Meta:
        model = PendingOrder
        exclude = ["user", "created_at"]
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['state'] = instance.state.name
        representation['lga'] = instance.lga.name
        representation['product'] = instance.product.uuid
        return representation
    def get_product_image(self, obj):
        request = self.context.get('request') 
        if request:
            return request.build_absolute_uri(obj.product.image.url)

    
    
class CompletedOrderSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()
    delivery_date = serializers.DateTimeField(format="%Y-%m-%d ")
    class Meta:
        model = CompletedOrder
        exclude = ["user", "created_at"]
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = instance.product.uuid
        return representation
    def get_product_image(self, obj):
        request = self.context.get('request') 
        if request:
            return request.build_absolute_uri(obj.product.image.url)

    
    
class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.CharField(write_only=True)

    class Meta:
        model = Favorite
        fields = ['product', 'product_id']
        read_only_fields = ['product']

    def create(self, validated_data):
        request = self.context.get('request')
        product_uuid = validated_data.pop('product_id')
        product = Product.objects.get(uuid=product_uuid)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
        return favorite
    