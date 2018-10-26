from django.db import models


class Driver(models.Model):
    name     =models.CharField(max_length=120)
    location =models.CharField(max_length=120,null=True,blank=True)
    driver_id=models.CharField(max_length=120)
    timestamp=models.DateTimeField(auto_now=False,auto_now_add=False)
