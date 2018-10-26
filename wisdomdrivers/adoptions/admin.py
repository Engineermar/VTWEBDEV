from django.contrib import admin

from .models import Drivers

@admin.register(Drivers)
class DriversAdmin(admin.ModelAdmin):
    list_display = ['name', 'sex', 'Drivers_ID',  'hire_date']
