"""agrigo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import url

from start import views


urlpatterns = [
    
    #url(r'^register/$', views.RegisterNewMember.as_view(), name='register'),
    url(r'^login/$', views.ULogin.as_view(), name='login'),
    url(r'^forgot-pwd/$', views.ForgotPwd.as_view(), name='forgot-pwd'),
 	url(r'^new-pwd/(?P<token>[0-9a-zA-Z]+)/(?P<email>[0-9a-zA-Z.@-_]+)/$', views.ResetPwd.as_view(), name='new-pwd'),
 	url(r'^activate/(?P<token>[0-9a-zA-Z]+)/(?P<email>[0-9a-zA-Z.@-_]+)/$', views.ActivateAccount.as_view(), name='activate'),
 	url(r'^resend-act-link/$', views.ResendActivationLink.as_view(), name='resend-act-link'),
    url(r'^mycafe/$', views.MyRights.as_view(), name='mycafe'),


    
    
]





