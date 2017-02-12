#!/usr/bin/env bash
#   Front-end to starting docker for OSX

# Get directory this is being run from
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Go there then go up
cd "${DIR}"
cd ..

# Do docker stuff
docker-compose up
