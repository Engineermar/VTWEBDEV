from __future__ import absolute_import, unicode_literals
from .base import *
DEBUG = False


ALLOWED_HOSTS = ['10.10.20.100:8000','10.10.20.100','localhost','localhost:8000','192.168.8.101']
WEB_ADDRESS='http://10.10.20.100:8000/' #backend
WEB_ADDRESS_FRONTEND='http://10.10.20.100/rlrc/' #front end

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': config('PRO_DB_NAME'),
        'USER': config('PRO_DB_USERNAME'),
        'PASSWORD': config('PRO_DB_PWD'),
        'HOST': config('PRO_DB_HOST'),   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

STATIC_URL = 'http://10.10.20.100/django_static/'

