#!/usr/bin/env bash
#   Shorthand to migrate and runserver in docker

# Needs to be done each time else SASS fails to bind
npm rebuild node-sass

python ./tabbycat/manage.py migrate --no-input
python ./tabbycat/manage.py runserver 0.0.0.0:8000