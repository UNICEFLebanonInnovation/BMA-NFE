# -*- coding: utf-8 -*-
"""
Production Configurations

- Use Amazon's S3 for storing static files and uploaded media
- Use mailgun to send emails
- Use Redis for cache
- Use sentry for error logging
- Use opbeat for error reporting

"""

from __future__ import absolute_import, unicode_literals
import logging

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env('DJANGO_SECRET_KEY')


# This ensures that Django will be able to detect a secure connection
# properly on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# raven sentry client
# See https://docs.sentry.io/clients/python/integrations/django/
# INSTALLED_APPS += ['raven.contrib.django.raven_compat','student_registration.accounts', ]
INSTALLED_APPS += ['student_registration.accounts', ]

# Use Whitenoise to serve static files
# See: https://whitenoise.readthedocs.io/
WHITENOISE_MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', ]
# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------


EXTRA_MIDDLEWARE = ['student_registration.middleware.AutoLogout',
                    'student_registration.cache_control_middleware.CacheControlMiddleware',
                    # 'student_registration.one_session.OneSessionPerUserMiddleware',
                    'student_registration.hsts_middleware.HSTSMiddleware',
                    'student_registration.xframe_middleware.XFrameMiddleware', ]
MIDDLEWARE = WHITENOISE_MIDDLEWARE + MIDDLEWARE + EXTRA_MIDDLEWARE


# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/en/dev/howto/deployment/checklist/#run-manage-py-check-deploy

# set this to 60 seconds and then to 518400 when you can prove it works
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_FRAME_DENY = env.bool("DJANGO_SECURE_FRAME_DENY", default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool('DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_PRELOAD = True

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])
CSRF_TRUSTED_ORIGINS = env.list('DJANGO_CSRF_TRUSTED_ORIGINS', default=[])
# END SITE CONFIGURATION

INSTALLED_APPS += ['gunicorn', ]

EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader', ]),
]

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------

# Use the Heroku-style specification
# Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
DATABASES['default'] = env.db('DATABASE_URL', default='postgres:///student_registration')

if env.bool('DATABASE_SSL_ENABLED', default=False):
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}

# CACHING
# ------------------------------------------------------------------------------
# CACHES = {
#     'default': {
#         # 'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': ''
#     }
# }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

# Sentry Configuration
SENTRY_DSN = env('DJANGO_SENTRY_DSN', default='')

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,  # Optional, for performance monitoring
    send_default_pii=True,   # Optional, if you want to send user info
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # Let Django's loggers work
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'level': 'WARNING',
        'handlers': ['console'],
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# Custom Admin URL, use {% url 'admin:index' %}
ADMIN_URL = env('DJANGO_ADMIN_URL', default='admin')

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'


# Auto logout delay in minutes
AUTO_LOGOUT_DELAY = 30  # equivalent to 30 minutes
CSRF_USE_SESSIONS = True

# ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
# ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 600
ACCOUNT_RATE_LIMITS = {
    "login_user": "10/m",
    "login_failed": "5/5m",
    "signup": "3/h",
    "email": "10/m",
    "password_change": "5/h",
}

CSRF_COOKIE_AGE = None

# Your production stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Maximum number of GET/POST parameters that will be read before a
# SuspiciousOperation (TooManyFieldsSent) is raised.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 4000
