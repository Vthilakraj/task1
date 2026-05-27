#!/usr/bin/env bash
set -e

pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py seed_movies --count 300
python manage.py collectstatic --noinput
