source env.example
export DJANGO_SETTINGS_MODULE=config.settings.test
python manage.py test student_registration.backends.tests
