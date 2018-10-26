from django.db import models

class Drivers(models.Model):

    name = models.CharField(max_length=100)
    SEX_CHOICES = [('M', 'Male'), ('F', 'Female')]
    sex = models.CharField(choices=SEX_CHOICES, max_length=1, blank=True)
    Drivers_ID = models.IntegerField(null=True)
  #  submitter = models.CharField(max_length=100)
    #species = models.CharField(max_length=30)
    #breed = models.CharField(max_length=30, blank=True)
    #description = models.TextField()

    hire_date = models.DateTimeField()



class Expenses(models.Model):
    Receipt_Type = models.CharField(max_length=50)
    Drivers_ID   = Drivers.Drivers_ID

    def __str__(self):
        return self.name
