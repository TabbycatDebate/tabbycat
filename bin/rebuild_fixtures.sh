#!/usr/bin/env bash

set -o errexit
dj flush
dj loaddata ./data/fixtures/$1.json
dj migrate
dj checkpreferences
dj dumpdata --natural-foreign --natural-primary \
            -e availability \
            -e contenttypes -e options -e options -e auth.Permission \
            -e admin.logentry -e actionlog.actionlogentry -e sessions \
            --indent 4 \
            --format=json -o data/fixtures/$1.json
