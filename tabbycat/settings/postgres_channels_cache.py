"""PostgreSQL-backed Channels layer and Django database cache.

Uses `channels_postgres <https://github.com/danidee10/channels_postgres>`_ for
WebSocket / group messaging and Django's built-in database cache backend for
page caching. Both use the same PostgreSQL database as ``DATABASES['default']``.
"""

from __future__ import annotations

import copy
from typing import Any

# Table for django.core.cache.backends.db.DatabaseCache (see createcachetable).
TABBYCAT_CACHE_TABLE = 'tabbycat_cache'


def postgres_database_cache() -> dict[str, dict[str, Any]]:
    return {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': TABBYCAT_CACHE_TABLE,
        },
    }


def postgres_channel_layers(
    default_db_config: dict[str, Any],
    *,
    group_expiry: int = 10800,
) -> dict[str, dict[str, Any]]:
    """Build CHANNEL_LAYERS for channels_postgres from a DATABASES['default']-style dict."""
    cfg = copy.deepcopy(default_db_config)

    # ``channels_postgres`` constructs Django's PostgreSQL DatabaseWrapper
    # directly, so it doesn't benefit from ConnectionHandler's normalisation of
    # DATABASES. Django 5.2's wrapper expects these keys to be present even when
    # their values are the defaults. Without TIME_ZONE in particular, Channels
    # catches the resulting KeyError and misleadingly reports that no channel
    # layer is configured.
    cfg.setdefault('OPTIONS', {})
    cfg.setdefault('TIME_ZONE', None)
    for setting in ('NAME', 'USER', 'PASSWORD', 'HOST', 'PORT'):
        cfg.setdefault(setting, '')

    return {
        'default': {
            'BACKEND': 'utils.channel_layers.SingleListenerPostgresChannelLayer',
            'CONFIG': {
                **cfg,
                'group_expiry': group_expiry,
            },
        },
    }
