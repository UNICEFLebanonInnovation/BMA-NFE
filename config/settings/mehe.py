"""MEHE Linux deployment: external PostgreSQL and the mounted VM file share."""
from .production import *  # noqa
from django.core.exceptions import ImproperlyConfigured

def required(name):
    value = env(name)
    if not value.strip() or 'CHANGE_ME' in value or value.startswith('<'):
        raise ImproperlyConfigured('{} must be configured for MEHE'.format(name))
    return value

SECRET_KEY = required('DJANGO_SECRET_KEY')
if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY must contain at least 50 characters')
DEBUG = False
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['172.16.2.101'])
CSRF_TRUSTED_ORIGINS = env.list('DJANGO_CSRF_TRUSTED_ORIGINS', default=['https://172.16.2.101'])
if not ALLOWED_HOSTS or '*' in ALLOWED_HOSTS:
    raise ImproperlyConfigured('Configure explicit DJANGO_ALLOWED_HOSTS for MEHE')
if not CSRF_TRUSTED_ORIGINS or any(not origin.startswith('https://') for origin in CSRF_TRUSTED_ORIGINS):
    raise ImproperlyConfigured('MEHE requires HTTPS origins')
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'HOST': env('MEHE_DB_HOST', default='192.168.41.30'),
    'PORT': env.int('MEHE_DB_PORT', default=5432),
    'NAME': required('MEHE_DB_NAME'),
    'USER': required('MEHE_DB_USER'),
    'PASSWORD': required('MEHE_DB_PASSWORD'),
    'CONN_MAX_AGE': 60,
    'OPTIONS': {'connect_timeout': 10, 'sslmode': env('MEHE_DB_SSLMODE', default='require')},
}}
if env('MEHE_DB_SSLROOTCERT', default=''):
    DATABASES['default']['OPTIONS']['sslrootcert'] = env('MEHE_DB_SSLROOTCERT')
NFE_FILE_SHARE_ROOT = env('NFE_FILE_SHARE_ROOT', default='/mnt/nfe-media')
NFE_REQUIRED_SHARE_SERVER = env('MEHE_FILE_SHARE_SERVER', default='192.168.41.31')
if not NFE_REQUIRED_SHARE_SERVER.strip():
    raise ImproperlyConfigured('MEHE_FILE_SHARE_SERVER must identify the actual file-share server')
MEDIA_ROOT = env('MEDIA_ROOT', default=NFE_FILE_SHARE_ROOT)
STORAGES = dict(STORAGES)
STORAGES['default'] = {'BACKEND': 'student_registration.media_storage.VMFileShareStorage'}
DEFAULT_FILE_STORAGE = STORAGES['default']['BACKEND']
MEDIA_URL = '/media/'
ROOT_URLCONF = 'config.mehe_urls'
ADMIN_URL = r'^admin/'
NFE_MEDIA_X_ACCEL_REDIRECT = env.bool('NFE_MEDIA_X_ACCEL_REDIRECT', default=True)
STATIC_ROOT = '/code/staticfiles'
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_TASK_ALWAYS_EAGER = False
CELERY_ALWAYS_EAGER = False
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
DATASYNC_INGEST_ENABLED = True
DATASYNC_PHOTO_INGEST_ENABLED = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
