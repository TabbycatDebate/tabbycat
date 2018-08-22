from __future__ import absolute_import, unicode_literals

# import os
# from django.conf import settings

from celery import Celery


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tabbycat.settings')

# The autoconfig settings wasn't working (commented-out portions)
# Directly define settings as a work around
# However then tasks.py files in projects don't seem to be imported nicely
app = Celery('tabbycat',
             broker='redis://localhost:6379',
             backend='redis://localhost:6379')


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
