#!/usr/bin/env bash
#   Shorthand to migrate and run honcho in docker

cd tabbycat

# Migrate (can't do it during build; no db connnection)
python ./manage.py migrate --no-input

# Needed to ensure daphne works properly
rm -f /tmp/asgi.socket /tmp/asgi.socket.lock

# Run honcho
cd ..
honcho -f ./ProcfileMulti.docker start
