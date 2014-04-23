#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
"""Development settings and globals."""

from os.path import join, normpath
from S3 import CallingFormat

from common import *


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
########## END EMAIL CONFIGURATION


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'karmanotes',
        'USER': 'djkarma',
        'PASSWORD': 'karma',
        'HOST': 'localhost',
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
    }
}
########## END DATABASE CONFIGURATION

########## STATIC CONFIG
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(DJANGO_ROOT, 'static'))

########## END STATIC CONFIG

########## CELERY CONFIGURATION
# See: http://docs.celeryq.org/en/latest/configuration.html#celery-always-eager
CELERY_ALWAYS_EAGER = True
########## END CELERY CONFIGURATION

########## STORAGE CONFIGURATION
# See: http://django-storages.readthedocs.org/en/latest/index.html
INSTALLED_APPS += (
    'storages',
)

# See: http://django-storages.readthedocs.org/en/latest/backends/amazon-S3.html#settings
AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN

# AWS cache settings, don't change unless you know what you're doing:
AWS_EXPIREY = 60 * 60 * 24 * 7
AWS_HEADERS = {
    'Cache-Control': 'max-age=%d, s-maxage=%d, must-revalidate' % (AWS_EXPIREY,
        AWS_EXPIREY)
}
########## END STORAGE CONFIGURATION


########## TOOLBAR CONFIGURATION
# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
INSTALLED_APPS += (
    'debug_toolbar',
    'django_extensions',
    'django_nose',
)

# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
INTERNAL_IPS = ('127.0.0.1',)

# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False # Don't interrput our redirects!
}
########## END TOOLBAR CONFIGURATION

########## COMPRESSION CONFIGURATION
COMPRESS_ENABLED = False
########## END COMPRESSION CONFIGURATION


########## TESTING CONFIGURATION
# Use django-nose to test our app, see https://github.com/jbalogh/django-nose
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
########## END TESTING CONFIGURATION
