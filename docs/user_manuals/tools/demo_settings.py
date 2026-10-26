from config.settings.local import *  # noqa
import os
S = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
MEDIA_ROOT = os.path.join(S, 'media')
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
ALLOWED_HOSTS = ['*']
DEBUG = True
DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': lambda request: False}
AUTO_LOGOUT_DELAY = 100000
