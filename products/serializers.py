from rest_framework import serializers
from .models import Category, Brand, Product, Deal
from users.models import Favorite


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories."""
    class Meta:
        model = Category
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for brands showing their linked categories by name."""
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Brand
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    """Main product serializer with UUID as ID and extra info."""
    id = serializers.UUIDField(source="uuid", read_only=True)
    category = serializers.StringRelatedField()
    brand = serializers.StringRelatedField()
    availabilityStatus = serializers.CharField(source="get_availability_status_display", read_only=True)
    conditionStatus = serializers.CharField(source="get_condition_display", read_only=True)
    user_wishlist = serializers.SerializerMethodField()

    class Meta:
        model = Product
        exclude = ["uuid", "availability_status", "condition"]

    def get_user_wishlist(self, obj):
        """Checks if this product is in the authenticated user's favorites."""
        user = self.context.get("request").user
        if user and user.is_authenticated:
            return Favorite.objects.filter(user=user, product=obj).exists()
        return False


class DealSerializer(serializers.ModelSerializer):
    """Serializer for special deals or promotions."""
    id = serializers.UUIDField(source="uuid", read_only=True)

    class Meta:
        model = Deal
        exclude = ["uuid"]
