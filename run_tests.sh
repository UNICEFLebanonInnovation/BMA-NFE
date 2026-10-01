#!/bin/sh
set -eu

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.test}"

coverage erase
coverage run manage.py test --noinput "$@"
coverage report --show-missing
