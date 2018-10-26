#Must be logged in to see this area
from django.conf.urls import  url

from techservices import views


urlpatterns = [
    url(r'^view/(?P<tag>[a-zA-Z0-9-]+)/(?P<searchby>[a-zA-Z0-9-]+)/$', views.Services.as_view(), name='view'),
    url(r'^add/(?P<tag>[a-zA-Z0-9-]+)/$', views.AddService.as_view(), name='add'),
    url(r'^edit/(?P<tag>[a-zA-Z0-9-]+)/(?P<service_id>[0-9]+)/$', views.EditService.as_view(), name='edit'),
    url(r'^delete/(?P<tag>[a-zA-Z0-9-]+)/(?P<service_id>[0-9]+)/$', views.DeleteService.as_view(), name='delete'),

]