#!/usr/bin/env bash
#   Shorthand to migrate and runserver in docker

# Move up to where we can run commands
cd tabbycat

# Migrate (can't do it during build; no db connnection)
python ./manage.py migrate --no-input

# Run the server
# python ./manage.py runserver 0.0.0.0:8000
waitress-serve --threads=12 --host=0.0.0.0 --port=8000 wsgi:application
