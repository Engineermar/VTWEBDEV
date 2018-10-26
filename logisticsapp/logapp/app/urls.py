"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from tools.company import productInformation
from app.conf import base as settings
from django.views.static import serve

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^hr/', include('hr.urls')),
    url(r'^inventory/', include('inventory.urls')),
    url(r'^start/', include('start.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^logistic/', include('logistic.urls')),
    url(r'^reports/', include('reports.urls')),
    url(r'^public/', include('public.urls')),
    url(r'^techservices/', include('techservices.urls')),
    url(r'^finder/', include('finder.urls')),
    url(r'^publish/', include('publisher.urls')),
    url(r'^account/', include('account.urls')),
    url(r'^messages/', include('messaging.urls')),
    url(r'^static/(?P<path>.*)$/', serve,{'document_root': settings.STATIC_ROOT },name="media"),
]

product_information=productInformation()

admin.site.site_header = product_information['company_name']
admin.site.site_title = product_information['company_name']
admin.site.index_title = product_information['product_name']




