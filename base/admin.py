from django.contrib import admin
from . import models


class LGAAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'delivery_days', 'delivery_fee')
    list_filter = ('delivery_days',)

admin.site.register(models.State) 
admin.site.register(models.LGA, LGAAdmin) 