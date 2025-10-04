from django.core.validators import RegexValidator
from django.db import models
from authentication.models import User
from base.models import State, LGA
from products.models import Product


class UserInfo(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_info")
	first_name = models.CharField(max_length=150, null=False)
	last_name = models.CharField(max_length=150, null=False)
	other_name = models.CharField(max_length=100, blank=True, null=True)
	alternative_email = models.EmailField(null=True, blank=True)
	alternative_phone_number = models.CharField(max_length=11, validators=[RegexValidator(r'^0\d{10}$', 'Mobile number should be 11 digits starting with 0.')])

	def __str__(self):
		return f"{self.first_name} - {self.last_name}"


class UserAddress(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_address")
	state = models.ForeignKey(State, on_delete=models.SET_NULL, related_name="user_state", null=True)
	city_town = models.CharField(max_length=30)
	lga = models.ForeignKey(LGA, on_delete=models.SET_NULL, related_name="user_lga", null=True)
	prominent_motor_park = models.CharField(max_length=50, null=True, blank=True)
	landmark_signatory_place = models.CharField(max_length=50, null=True, blank=True)
	address = models.TextField()
	def __str__(self):
		return f"{self.user} - {self.address}"


class PendingOrder(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_pending_order")
	# Delivery Info
	name = models.CharField(max_length=100)
	phone_number = models.CharField(max_length=11, validators=[RegexValidator(r'^0\d{10}$', 'Mobile number should be 11 digits starting with 0.')])
	state = models.ForeignKey(State, on_delete=models.SET_NULL, related_name="state_pending_order", null=True)
	city_town = models.CharField(max_length=30)
	lga = models.ForeignKey(LGA, on_delete=models.SET_NULL, related_name="lga_pending_order", null=True)
	prominent_motor_park = models.CharField(max_length=50, null=True, blank=True)
	landmark_signatory_place = models.CharField(max_length=50, null=True, blank=True)
	address = models.TextField()
	# Product Info
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name="product_pending_order", null=True)
	price = models.IntegerField()
	quantity = models.IntegerField()
	product_name = models.CharField(max_length=200)
	shipped = models.BooleanField(default=False)
	estimated_delivery_date = models.DateTimeField()
	created_at = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return f"{self.user} - {self.product.name}"
	
	class Meta:
		ordering = ['-created_at']

class CompletedOrder(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_completed_order")
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name="product_completed_order", null=True)
	price = models.IntegerField()
	product_name = models.CharField(max_length=200)
	quantity = models.IntegerField()
	delivery_date = models.DateTimeField()
	address = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.user} - {self.product_name}"

	class Meta:
		ordering = ['-created_at']

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.email} favorited {self.product.name}'
