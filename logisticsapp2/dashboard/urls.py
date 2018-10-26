#Must be logged in to see this area
from django.conf.urls import  url

from dashboard import views


urlpatterns = [
    url(r'^employee/$', views.Employee.as_view(), name='employee')


]