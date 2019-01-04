"""
WSGI config for mitoage project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mitoage.settings")

from django.core.wsgi import get_wsgi_application


def application(environ, start_response):
    # pass the WSGI environment variables on through to os.environ
    for key in environ:
        if key.startswith('MYAPP_'):
            os.environ[key] = environ[key]

    application = get_wsgi_application()

    return application(environ, start_response)
