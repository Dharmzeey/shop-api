from  django.contrib  import  admin
from .models  import  Payment

class  PaymentAdmin(admin.ModelAdmin):
    list_display  = ["ref", 'amount', "verified", "date_created"]

admin.site.register(Payment, PaymentAdmin)
