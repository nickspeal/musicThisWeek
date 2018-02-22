"""
WSGI config for musicThisWeek project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "musicThisWeek.settings")

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
print("Found this secret key as an environment variable: ", SECRET_KEY)
application = get_wsgi_application()
