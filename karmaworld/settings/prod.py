#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
""" Production settings and globals. """
from os import environ
from datetime import timedelta
from S3 import CallingFormat

from common import *

from karmaworld.secret.db_settings import PROD_DB_NAME
from karmaworld.secret.db_settings import PROD_DB_USERNAME
from karmaworld.secret.db_settings import PROD_DB_PASSWORD

try:
    # Include email is settings are there
    from karmaworld.secret.email import SMTP_HOST
    from karmaworld.secret.email import SMTP_USERNAME
    from karmaworld.secret.email import SMTP_PASSWORD
    EMAIL = True
except:
    EMAIL = False

########## EMAIL CONFIGURATION
if EMAIL:
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
    EMAIL_HOST = environ.get('EMAIL_HOST', SMTP_HOST)
    
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
    EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', SMTP_PASSWORD)
    
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
    EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', SMTP_USERNAME)
    
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
    EMAIL_PORT = environ.get('EMAIL_PORT', 587)
    
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
    EMAIL_SUBJECT_PREFIX = 'KarmaNotes '
    
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
    EMAIL_USE_TLS = True
    
    DEFAULT_FROM_EMAIL = 'info@karmanotes.org'
    
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
    SERVER_EMAIL = EMAIL_HOST_USER
########## END EMAIL CONFIGURATION


########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': PROD_DB_NAME,
    'USER': PROD_DB_USERNAME,
    'PASSWORD': PROD_DB_PASSWORD,
    'HOST': '',
    'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211'
    }
}
########## END CACHE CONFIGURATION


########## CELERY CONFIGURATION
# See: http://docs.celeryproject.org/en/latest/configuration.html#broker-transport
BROKER_TRANSPORT = 'amqplib'

# Set this number to the amount of allowed concurrent connections on your AMQP
# provider, divided by the amount of active workers you have.
#
# For example, if you have the 'Little Lemur' CloudAMQP plan (their free tier),
# they allow 3 concurrent connections. So if you run a single worker, you'd
# want this number to be 3. If you had 3 workers running, you'd lower this
# number to 1, since 3 workers each maintaining one open connection = 3
# connections total.
#
# See: http://docs.celeryproject.org/en/latest/configuration.html#broker-pool-limit
BROKER_POOL_LIMIT = 3

# See: http://docs.celeryproject.org/en/latest/configuration.html#broker-connection-max-retries
BROKER_CONNECTION_MAX_RETRIES = 0

# See: http://docs.celeryproject.org/en/latest/configuration.html#broker-url
BROKER_URL = environ.get('RABBITMQ_URL') or environ.get('CLOUDAMQP_URL')

# See: http://docs.celeryproject.org/en/latest/configuration.html#celery-result-backend
CELERY_RESULT_BACKEND = 'amqp'

# Periodic tasks
CELERYBEAT_SCHEDULE = {
    'tweet-about-notes': {
        'task': 'tweet_note',
        'schedule': timedelta(minutes=60),
    },
}

CELERY_TIMEZONE = 'UTC'

########## END CELERY CONFIGURATION


########## STORAGE CONFIGURATION
# See: http://django-storages.readthedocs.org/en/latest/index.html
INSTALLED_APPS += (
    'storages',
    'gunicorn',
)

# See: http://django-storages.readthedocs.org/en/latest/backends/amazon-S3.html#settings
# DEFAULT_FILE_STORAGE comes from karmaworld.secret.static_s3
STATICFILES_STORAGE = DEFAULT_FILE_STORAGE

# Put static files in the folder 'static' in our S3 bucket.
# This is so they have the same path as they do when served
# locally for development.
AWS_LOCATION = 'static'

# See: http://django-storages.readthedocs.org/en/latest/backends/amazon-S3.html#settings
AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN

# AWS cache settings, don't change unless you know what you're doing:
AWS_EXPIREY = 60 * 60 * 24 * 7
AWS_HEADERS = {
    'Cache-Control': 'max-age=%d, s-maxage=%d, must-revalidate' % (AWS_EXPIREY,
        AWS_EXPIREY)
}

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
# S3_URL comes from karmaworld.secret.static_s3
STATIC_URL = CLOUDFRONT_URL + '/' + AWS_LOCATION + '/'
########## END STORAGE CONFIGURATION

########## SSL FORWARDING CONFIGURATION
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
########## END SSL FORWARDING CONFIGURATION

########## COMPRESSION CONFIGURATION
# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_OFFLINE
COMPRESS_OFFLINE = True

# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_STORAGE
COMPRESS_STORAGE = DEFAULT_FILE_STORAGE

# Make sure that django-compressor serves from CloudFront
AWS_S3_CUSTOM_DOMAIN = CLOUDFRONT_DOMAIN

# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_CSS_FILTERS
COMPRESS_CSS_FILTERS += [
    'compressor.filters.datauri.CssDataUriFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_DATA_URI_MAX_SIZE = 5120

# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_JS_FILTERS
COMPRESS_JS_FILTERS += [
    'compressor.filters.closure.ClosureCompilerFilter',
]
COMPRESS_CLOSURE_COMPILER_BINARY = 'java -jar /usr/bin/compiler.jar'

# Links generated by compress are valid for about ten years
AWS_QUERYSTRING_EXPIRE = 60 * 60 * 24 * 365 * 10
########## END COMPRESSION CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = environ.get('SECRET_KEY', SECRET_KEY)
########## END SECRET CONFIGURATION
