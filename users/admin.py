from django.contrib import admin
from . import models


admin.site.register(models.UserInfo)
admin.site.register(models.UserAddress)
admin.site.register(models.PendingOrder)
admin.site.register(models.CompletedOrder)

# class FavouriteAdmin(admin.ModelAdmin):
#     list_display = ["user", "product"]
admin.site.register(models.Favorite)