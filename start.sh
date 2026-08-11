#!/usr/bin/env bash
set -o errexit

# Apply pending migrations. On a freshly created Render database a plain
# `migrate` is enough (nothing is applied yet, so the custom-user upgrade
# paths in accounts/migrations are exercised for a clean install).
# If you later restore an OLD database that already has auth_user/admin
# migrations applied, run `python manage.py bootstrap_user_model` first.
python manage.py migrate

gunicorn collegePortal.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 1 --timeout 120
