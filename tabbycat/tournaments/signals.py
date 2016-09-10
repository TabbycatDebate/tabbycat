from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from tournaments.models import Round, Tournament

import logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Tournament)
def update_tournament_cache(sender, instance, **kwargs):
    cached_key = "%s_%s" % (instance.slug, 'object')
    cache.delete(cached_key)
    cached_key = "%s_%s" % (instance.slug, 'current_round_object')
    cache.delete(cached_key)


@receiver(post_save, sender=Round)
def update_round_cache(sender, instance, **kwargs):
    cached_key = "%s_%s_%s" % (instance.tournament.slug, instance.seq,
                               'object')
    cache.delete(cached_key)
    logger.debug("Updated cache %s for %s" % (cached_key, instance))

    if instance.tournament.current_round_id == instance.id:
        logger.debug("Updating tournament cache because %s is the current round" % instance)
        update_tournament_cache(sender, instance.tournament, **kwargs)
