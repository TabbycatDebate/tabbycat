#!/usr/bin/env bash

dj loaddata ./data/fixtures/completed_demo.json
dj migrate
dj checkpreferences
dj dumpdata --natural-foreign --natural-primary -e options -e sessions -e contenttypes --format=json -o data/fixtures/completed_demo.json