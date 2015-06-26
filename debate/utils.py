import string, random
from django.db import IntegrityError
import logging
logger = logging.getLogger(__name__)

def generate_url_hash(length=8):
    """Generates a URL hash."""
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

def populate_url_hashes(queryset, length=8):
    """Populates the URL hash field for every instance in the given QuerySet."""
    NUM_ATTEMPTS = 10
    for instance in queryset:
        for i in range(NUM_ATTEMPTS):
            instance.url_hash = generate_url_hash(length)
            try:
                instance.save()
            except IntegrityError:
                logger.warning("URL hash was not unique, trying again (%d of %d", i, NUM_ATTEMPTS)
                continue
            else:
                break
        else:
            logger.error("Could not generate unique URL for %r after %d tries", instance, NUM_ATTEMPTS)
            return

def delete_url_hashes(queryset):
    """Deletes URL hashes from every instance in the given QuerySet."""
    for instance in queryset:
        instance.url_hash = None
        instance.save()
