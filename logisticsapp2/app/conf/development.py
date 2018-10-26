from .base import *

DEBUG = True

ALLOWED_HOSTS = []

WEB_ADDRESS='http://localhost:9010/' #backend
WEB_ADDRESS_FRONTEND='http://localhost:4400/' #front end

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': config('DEV_DB_NAME'),
        'USER': config('DEV_DB_USERNAME'),
        'PASSWORD': config('DEV_DB_PWD'),
        'HOST': config('DEV_DB_HOST'),   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

STATIC_URL = '/static/'
