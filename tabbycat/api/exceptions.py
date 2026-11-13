import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from utils.sentry import get_sentry_trace_id

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    """Return JSON for unhandled errors instead of letting Django serve the HTML 500 page."""
    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    if settings.DEBUG:
        return

    logger.exception("Unhandled exception in API request")

    data = {'detail': 'A server error occurred.'}
    trace_id = get_sentry_trace_id()
    if trace_id:
        data['sentry_trace_id'] = trace_id

    return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
