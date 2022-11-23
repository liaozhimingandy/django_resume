#!/bin/sh

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py makemigrations resume
python manage.py migrate

exec "$@"
