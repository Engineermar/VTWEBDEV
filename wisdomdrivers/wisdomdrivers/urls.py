from django.conf.urls import url
from django.contrib import admin

from adoptions import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    #url(r'^adoptions/(\d+)/', views.driver_detail, name='driver_detail'),
    url(r'^adoptions/(\d+)/', views.driver_detail, name='driver_detail'),
]
