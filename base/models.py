from django.db import models


class State(models.Model):
  name = models.CharField(max_length=20)  
  def __str__(self):
    return self.name
  
  class Meta:
    ordering = ["name"]
      

class LGA(models.Model):
  state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, related_name="state_lga")
  name = models.CharField(max_length=50)  
  delivery_days = models.IntegerField()
  delivery_fee = models.IntegerField()
  def __str__(self):
    return self.name
  
  class Meta:
    ordering = ["name"]
  