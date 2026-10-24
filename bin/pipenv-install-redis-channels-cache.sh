#!/usr/bin/env bash
# Install Pipfile category [redis-channels-cache] when TABBYCAT_USE_REDIS_CHANNELS_CACHE
# is set (same truthiness as tabbycat.settings.heroku._truthy_env).
set -eo pipefail

val="${TABBYCAT_USE_REDIS_CHANNELS_CACHE:-}"
lc=$(printf '%s' "$val" | tr '[:upper:]' '[:lower:]')
case "$lc" in
  1|true|yes)
    command -v pipenv >/dev/null 2>&1 || python -m pip install pipenv
    pipenv install --system --categories=redis-channels-cache "$@"
    ;;
esac
