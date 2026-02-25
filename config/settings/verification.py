from config.settings.local import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable some middleware that might cause issues in sandbox
MIDDLEWARE = [m for m in MIDDLEWARE if 'DebugToolbarMiddleware' not in m]
INSTALLED_APPS = [app for app in INSTALLED_APPS if 'debug_toolbar' not in app]
