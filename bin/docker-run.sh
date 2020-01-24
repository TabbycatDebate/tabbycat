#!/usr/bin/env bash
#   Shorthand to migrate and runserver in docker

# Move up to where we can run commands
cd tabbycat

# Migrate (can't do it during build; no db connnection)
python ./manage.py migrate --no-input

npm run build

# Run the server
python ./manage.py runserver 0.0.0.0:8000
