from django.db import models



# Create your models here.

class Country(models.Model):
	'''
	List of countries goes here. This is useful in Employee model
	'''
	iso=models.CharField(max_length=2,unique=True)
	name=models.CharField(max_length=55,unique=True)
	phonecode=models.PositiveIntegerField()
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)





