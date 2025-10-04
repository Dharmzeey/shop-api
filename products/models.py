import uuid
from django.db import models


class Category(models.Model):
  name = models.CharField(max_length=30)

  class Meta:
    verbose_name_plural = "Categories"
  
  def __str__(self):
    return self.name
    

class Brand(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=30)
    
    def __str__(self):
        return self.name
  
class Product(models.Model):
    AVAILABILITY_STATUS_AVAILABLE = 1
    AVAILABILITY_STATUS_UNAVAILABLE = 0

    UTILIZATION_STATUS_BRAND_NEW = 0
    UTILIZATION_STATUS_UK_USED = 1


    AVAILABILITY_STATUS_CHOICES = (
        (AVAILABILITY_STATUS_AVAILABLE,"Available"),
        (AVAILABILITY_STATUS_UNAVAILABLE, "Unavailable")
    )
    UTILIZATION_STATUS_CHOICES = (
        (UTILIZATION_STATUS_BRAND_NEW,"Brand New"),
        (UTILIZATION_STATUS_UK_USED, "UK Used")
    )
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=225)
    description = models.TextField()
    price = models.IntegerField()
    image = models.ImageField(upload_to="products/%Y/%m")
    stock = models.IntegerField()
    availability_status = models.IntegerField(choices=AVAILABILITY_STATUS_CHOICES)
    utilization_status = models.IntegerField(choices=UTILIZATION_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
  

class Deal(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=200)
    details = models.TextField()
    image = models.ImageField(upload_to="deals/%Y/%m")
    link_to = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title