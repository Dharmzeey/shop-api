from django.db import models
from users.models import User
from .paystack  import  Paystack


# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payment')
    amount = models.PositiveIntegerField()
    email = models.EmailField()
    access_code = models.CharField(max_length=30)
    ref = models.CharField(max_length=30)
    session_id = models.CharField(max_length=100) # this will be the id to the session db so as to later query the products and address
    session_data = models.TextField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return f"User: {self.user} - Payment: {self.amount}"

    # def save(self, *args, **kwargs):
    #     while not self.ref:
    #         ref = secrets.token_urlsafe(50)
    #         object_with_similar_ref = Payment.objects.filter(ref=ref)
    #         if not object_with_similar_ref:
    #             self.ref = ref

    #     super().save(*args, **kwargs)
        
    def amount_value(self):
        return int(self.amount) * 100
    
    def verify_payment(self):
        self.verified = True
        self.save()
        if self.verified:
            return True
        return False
