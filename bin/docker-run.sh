#!/usr/bin/env bash
#   Shorthand to migrate and runserver in docker

python ./tabbycat/manage.py migrate --no-input
python ./tabbycat/manage.py runserver 0.0.0.0:8000