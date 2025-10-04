from django.contrib import admin
from .models import Category, Brand,Product, Deal

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Deal)