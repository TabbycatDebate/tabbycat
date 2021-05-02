import logging
import string

from participants.models import Person
from utils.misc import generate_identifier_string

logger = logging.getLogger(__name__)


def populate_url_keys(people, length=8, num_attempts=10):
    """Populates the URL key field for every instance in the given QuerySet."""
    chars = string.ascii_lowercase + string.digits

    existing_keys = list(Person.objects.exclude(url_key__isnull=True).values_list('url_key', flat=True))
    for person in people:
        for i in range(num_attempts):
            new_key = generate_identifier_string(chars, length)
            if new_key not in existing_keys:
                person.url_key = new_key
                existing_keys.append(new_key)
                break
        else:
            logger.error("Could not generate unique URL for %r after %d tries", person, num_attempts)
    Person.objects.bulk_update(people, ['url_key'])


def delete_url_keys(queryset):
    """Deletes URL keys from every instance in the given QuerySet."""
    queryset.update(url_key=None)
