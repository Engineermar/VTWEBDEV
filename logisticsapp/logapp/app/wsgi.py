"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""


import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.conf.production")

#DJANGO_SETTINGS_MODULE="app.conf.production"
os.environ['DJANGO_SETTINGS_MODULE'] = 'app.conf.production'

application = get_wsgi_application()



