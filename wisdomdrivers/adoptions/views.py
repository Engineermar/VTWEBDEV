from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404

from .models import Drivers

def home(request):
    drivers = Drivers.objects.all()
    return render(request, 'home.html', {'drivers': drivers})

def driver_detail(request, id):
    try:
        driver = Drivers.objects.get(id=id)
    except driver.DoesNotExist:
        raise Http404('driver not found')
    return render(request, 'driver_detail.html', {'driver': driver})
