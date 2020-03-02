import logging

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from tournaments.models import Round, Tournament

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Tournament)
def update_tournament_cache(sender, instance, **kwargs):
    cached_key = "%s_%s" % (instance.slug, 'object')
    cache.delete(cached_key)
    cached_key = "%s_%s" % (instance.slug, 'current_round_object')
    cache.delete(cached_key)


@receiver(post_delete, sender=Round)
@receiver(post_save, sender=Round)
def update_round_cache(sender, instance, **kwargs):
    cached_key = "%s_%s_%s" % (instance.tournament.slug, instance.seq, 'object')
    cache.delete(cached_key)
    logger.debug("Cleared cache %s for %s" % (cached_key, instance))

    # Update the tournament cache as well if either this is the current round,
    # or the current round is None (this might mean the current round was deleted).
    current_round_id = getattr(instance.tournament.current_round, 'id', None)
    if current_round_id == instance.id or current_round_id is None:
        logger.debug("Cleared %s tournament cache because the current round is %s" %
                (instance.tournament.slug, instance if current_round_id == instance.id else current_round_id))
        update_tournament_cache(sender, instance.tournament, **kwargs)
