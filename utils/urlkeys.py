import string
import random
import logging
from django.db import IntegrityError
logger = logging.getLogger(__name__)


def generate_url_key(length=8):
    """Generates a randomised URL key."""
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


def populate_url_keys(queryset, length=8):
    """Populates the URL key field for every instance in the given QuerySet."""
    num_attempts = 10
    for instance in queryset:
        for i in range(num_attempts):
            instance.url_key = generate_url_key(length)
            try:
                instance.save()
            except IntegrityError:
                logger.warning(
                    "URL key was not unique, trying again (%d of %d", i,
                    num_attempts)
                continue
            else:
                break
        else:
            logger.error("Could not generate unique URL for %r after %d tries",
                         instance, num_attempts)
            return


def delete_url_keys(queryset):
    """Deletes URL keys from every instance in the given QuerySet."""
    for instance in queryset:
        instance.url_key = None
        instance.save()
