#!/usr/bin/env bash
#   Front-end to starting docker for OSX

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd "${DIR}"
cd ..
docker-compose up