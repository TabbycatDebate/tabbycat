import logging


class ExceptFilter(logging.Filter):
    """The negative of the base Python filter: Only allows records *not* below
    a certain point in the logger hierarchy.
    See: https://docs.python.org/3/library/logging.html#filter-objects
    """

    def filter(self, record):
        return not super().filter(record)


def sentry_before_send(event, hint):
    """Keep useful warning events without sending routine Django 404s to Sentry."""
    record = hint.get('log_record')
    if record is not None and record.name == 'django.request' and getattr(record, 'status_code', None) == 404:
        return None
    return event
