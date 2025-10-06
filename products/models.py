import uuid
from django.db import models


class Category(models.Model):
    """Represents a general product category like Electronics, Fashion, etc."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Brand(models.Model):
    """Represents product brands (can belong to multiple categories)."""
    name = models.CharField(max_length=100, unique=True)
    categories = models.ManyToManyField(Category, related_name="brands", blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Generalized Product Model for all product types."""
    AVAILABILITY_CHOICES = [
        (1, "Available"),
        (0, "Unavailable"),
    ]
    CONDITION_CHOICES = [
        (0, "Brand New"),
        (1, "Used"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to="products", blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    availability_status = models.IntegerField(choices=AVAILABILITY_CHOICES, default=1)
    condition = models.IntegerField(choices=CONDITION_CHOICES, default=0)

    # Product variations (e.g., sizes, colors)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    weight = models.IntegerField(null=True, blank=True, help_text="Weight in kg")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Deal(models.Model):
    """Special deals, promotions, or campaigns."""
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    image = models.ImageField(upload_to="deals", blank=True, null=True)
    link_to = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
