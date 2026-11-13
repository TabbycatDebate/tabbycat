import sentry_sdk


def get_sentry_trace_id():
    if sentry_sdk.is_initialized():
        return sentry_sdk.get_current_scope().get_trace_context().get('trace_id')
    return None
