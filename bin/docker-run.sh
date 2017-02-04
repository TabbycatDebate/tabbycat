#!/usr/bin/env bash
#   Shorthand to migrate and runserver in docker

cd tabbycat
python ./manage.py migrate --no-input
waitress-serve --threads=12 --host=0.0.0.0 --port=8000 wsgi:application