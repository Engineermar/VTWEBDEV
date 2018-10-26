#Must be logged in to see this area
from django.conf.urls import  url

from publisher import views



urlpatterns = [
    url(r'^publish/(?P<publish_what>[0-9]+)/$', views.Publish.as_view(), name='publish'),


]