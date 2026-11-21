import logging

from django.test import SimpleTestCase

from .logging import sentry_before_send


class SentryEventFilterTests(SimpleTestCase):
    def test_filters_only_django_not_found_logs(self):
        event = {'message': 'event'}
        for logger, status, level, expected in (
            ('django.request', 404, logging.WARNING, None),
            ('django.request', 403, logging.WARNING, event),
            ('django.request', 500, logging.ERROR, event),
            ('portal', 404, logging.WARNING, event),
        ):
            with self.subTest(logger=logger, status=status):
                record = logging.LogRecord(logger, level, '', 0, 'message', (), None)
                record.status_code = status
                self.assertEqual(sentry_before_send(event, {'log_record': record}), expected)
        self.assertEqual(sentry_before_send(event, {}), event)
