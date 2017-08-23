from django.conf import settings
from raven.contrib.django.raven_compat import DjangoClient
from raven.contrib.django.utils import get_host


class TabbycatRavenClient(DjangoClient):
    """Makes the user ID the e-mail address, rather than the primary key."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add tab director e-mail to extra context
        if hasattr(settings, 'TAB_DIRECTOR_EMAIL'):
            self.extra_context({'tab_director_email': settings.TAB_DIRECTOR_EMAIL})

    def get_data_from_request(self, request):
        """Override the user ID with the e-mail address if it exists, or append
        the host name if it does not exist.

        The base implementation can be found at:
        https://github.com/getsentry/raven-python/blob/master/raven/contrib/django/client.py
        """

        result = super().get_data_from_request(request)

        try:
            user_info = result.get('user')
            if user_info:
                if user_info.get('email'):
                    # If there's an e-mail address, just use it.
                    user_info['id'] = user_info['email']
                else:
                    # Otherwise, append the host name.
                    host = get_host(request)
                    user_info['id'] = "%s@%s" % (user_info['id'], host)
        except Exception:
            # Just make best efforts; if it all fell apart, so be it.
            pass

        return result
