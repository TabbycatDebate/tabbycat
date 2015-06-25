from functools import wraps
import string, random
from django.db import IntegrityError
import logging
logger = logging.getLogger(__name__)

def gen_results():
    r = {'aff': (0,), 'neg': (0,)}

    def do():
        s = [random.randint(60, 80) for i in range(3)]
        s.append(random.randint(30,40))
        return s

    while sum(r['aff']) == sum(r['neg']):
        r['aff'] = do()
        r['neg'] = do()

    return r

def make_dummy_speakers():
    from debate import models as m
    t = m.Tournament.objects.get(pk=1)

    for team in t.teams:
        assert m.Speaker.objects.filter(team=team).count() == 0
        for i in range(1, 4):
            m.Speaker(name='%s %d' % (team, i), team=team).save()

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
