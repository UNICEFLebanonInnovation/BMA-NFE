# -*- coding: utf-8 -*-
"""
Django settings for Student Registration project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals

import environ
import os
import logging
import importlib.util
from kombu import Queue

logger = logging.getLogger(__name__)

ROOT_DIR = environ.Path(__file__) - 3  # (student_registration/config/settings/base.py - 3 = student_registration/)
APPS_DIR = ROOT_DIR.path('student_registration')

# Load operating system environment variables and then prepare to use them
env = environ.Env()

#Version
COMPILER_VERSION = '2.35'

# .env file, should load only in development environment
READ_DOT_ENV_FILE = env.bool('DJANGO_READ_DOT_ENV_FILE', default=False)

if READ_DOT_ENV_FILE:
    # Operating System Environment variables have precedence over variables defined in the .env file,
    # that is to say variables from the .env files will only be used if not defined
    # as environment variables.
    env_file = str(ROOT_DIR.path('.env'))
    logger.info('Loading : %s', env_file)
    env.read_env(env_file)
    logger.info('The .env file has been loaded. See base.py for more information')


# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    'django.contrib.humanize',

    'dal',
    'dal_select2',

    # Admin
    'jazzmin',
    'django.contrib.admin',
    'prettyjson',
    #'storages'
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_bootstrap3",
    # "crispy_bootstrap5",
    # "crispy_bootstrap4",
    'allauth',  # registration
    'allauth.account',  # registration
    'allauth.socialaccount',  # registration
    'rest_framework',
    'drf_spectacular',
    'rest_framework.authtoken',
    'django_makemessages_xgettext',

    'django_bootstrap5',
    # 'bootstrap4',
    'bootstrap3_datetime',
    'import_export',
    'django_tables2',
    'django_celery_beat',
    'django_celery_results',
    'six',
]



TAILWIND_APPS = []
if importlib.util.find_spec('tailwind') is not None:
    TAILWIND_APPS.append('tailwind')
TAILWIND_APPS.append('student_registration.theme')

# Apps specific for this project go here.
LOCAL_APPS = [
    'student_registration.users',  # custom users app
    'student_registration.students',  # custom students app
    'student_registration.clm',  # custom clm app
    'student_registration.attendances',  # custom attendances app
    'student_registration.schools',  # custom schools app
    'student_registration.locations',  # custom locations app
    'student_registration.dashboard',  # custom dashboard app
    'student_registration.backends',  # custom storage app
    'student_registration.child',
    'student_registration.mscc',
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + TAILWIND_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # "whitenoise.middleware.WhiteNoiseMiddleware",
    # "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "student_registration.user_activity.UserActivityMiddleware",
    # "social_django.middleware.SocialAuthExceptionMiddleware",
]

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {
    'sites': 'student_registration.contrib.sites.migrations'
}

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

IMPORT_EXPORT_USE_TRANSACTIONS = False
IMPORT_EXPORT_SKIP_ADMIN_LOG = False

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ("""UNICEF Lebanon Innovation""", 'achamseddine@unicef.org'),
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres:///student_registration'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True

DJANGO_READ_DOT_ENV_FILE = True

# DATABASES['default']['ATOMIC_REQUESTS'] = True

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Beirut'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = False

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                # 'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap3", "bootstrap5"]
# CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap3"

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(APPS_DIR.path('static')),
]

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# PASSWORD STORAGE SETTINGS
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {'NAME': 'student_registration.password_validators.NumberValidator',
     'OPTIONS': {
         'min_digits': 3, }},
    {'NAME': 'student_registration.password_validators.UppercaseValidator', },
    {'NAME': 'student_registration.password_validators.LowercaseValidator', },
    {'NAME': 'student_registration.password_validators.SymbolValidator', },
]

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Some really nice defaults
# ACCOUNT_LOGIN_METHODS = 'username'
ACCOUNT_LOGIN_METHODS = {'username'}
# ACCOUNT_AUTHENTICATION_METHOD = 'username'
# ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_SIGNUP_FIELDS = ['email', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'none'

ACCOUNT_ALLOW_REGISTRATION = env.bool('DJANGO_ACCOUNT_ALLOW_REGISTRATION', True)
ACCOUNT_ADAPTER = 'student_registration.users.adapters.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'student_registration.users.adapters.SocialAccountAdapter'

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'login_success'
# LOGIN_REDIRECT_URL = 'users:redirect'
LOGIN_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'

########## CELERY
INSTALLED_APPS += ['student_registration.taskapp.celery.CeleryConfig']
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_QUEUES = (
    Queue('default', routing_key='default'),
    Queue('mscc_export', routing_key='mscc_export'),
)
CELERY_TASK_ROUTES = {
    'student_registration.mscc.tasks.generate_mscc_export': {
        'queue': 'mscc_export',
        'routing_key': 'mscc_export',
    },
}
########## END CELERY

# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r'^admin/'

# Your common stuff: Below this line define 3rd party library settings

LOCALE_PATHS = [
    str(APPS_DIR.path('static/locale')),
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # this setting fixes the bug where user can be logged in as AnonymousUser
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'BMA API',
    'DESCRIPTION': 'API for the BMA project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,  # Usually True for Swagger UI/Redoc
    'POSTPROCESSING_HOOKS': [],
    # OTHER SETTINGS AS NEEDED
}

JAZZMIN_SETTINGS = {
    "site_title": "BMA",
    "site_header": "BMA-2",
    "welcome_sign": "Welcome, Admin",
    "copyright": "UNICEF",
    "show_sidebar": True,
    "navigation_expanded": True,
    "topmenu_links": [
        {"app": "users"},
        {"app": "backends"},
        {"app": "mscc"},
        {"app": "youth"},
        {"app": "clm"},
        {"app": "locations"},
        {"app": "schools"},
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
}

# STORAGE CONFIGURATION
# ------------------------------------------------------------------------------
# Uploaded Media Files
# ------------------------
# See: http://django-storages.readthedocs.io/en/latest/index.html
INSTALLED_APPS += ['storages', ]

AZURE_ACCOUNT_NAME = env('AZURE_ACCOUNT_NAME', default='NO_AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = env('AZURE_ACCOUNT_KEY', default='NO_AZURE_ACCOUNT_KEY')
AZURE_CONTAINER = env('AZURE_CONTAINER', default='NO_AZURE_CONTAINER')

DEFAULT_FILE_STORAGE = 'storages.backends.azure_blob.AzureBlobStorage' # Updated for newer django-storages
DEFAULT_FILE_FORMAT = 'xlsx'
DEFAULT_FILE_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
DEFAULT_FILE_CONTENT_LANGUAGE = 'ar'

UNIQUE_ID_API_TOKEN_URL = env('UNIQUE_ID_API_TOKEN_URL', default='https://leb-cash-ims.azurewebsites.net/cashmis/api/auth/getAccessToken')
UNIQUE_ID_API_URL = env('UNIQUE_ID_API_URL', default='https://leb-cash-ims.azurewebsites.net/cashmis/api/Request/getIndividualsUniqueIDs')
UNIQUE_PROGRAMMES_API_URL = env('UNIQUE_PROGRAMMES_API_URL', default='https://leb-cash-ims.azurewebsites.net/cashmis/api/Request/getIndividualsProgrammes')
UNIQUE_ID_API_USERNAME = env('UNIQUE_ID_API_USERNAME', default='NO_USERNAME')
UNIQUE_ID_API_PASSWORD = env('UNIQUE_ID_API_PASSWORD', default='NO_PASSWORD')

# import firebase_admin
# from firebase_admin import credentials
# from pathlib import Path
#
# root_dirt = Path(__file__).parents[2]
# FIREBASE_CREDENTIALS_FILE = os.path.join(str(root_dirt / "utility"), 'firebase-creds.json')
# cred = credentials.Certificate(FIREBASE_CREDENTIALS_FILE)
# firebase_app = firebase_admin.initialize_app(cred)

TAILWIND_APP_NAME = 'theme'
