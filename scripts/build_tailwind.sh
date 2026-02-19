#!/usr/bin/env bash
set -euo pipefail
npx tailwindcss -i ./student_registration/static/src/tailwind-input.css -o ./student_registration/static/css/tailwind.css --minify
