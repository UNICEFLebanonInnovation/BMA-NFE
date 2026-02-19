#!/usr/bin/env bash
set -euo pipefail
python manage.py tailwind install
python manage.py tailwind build
