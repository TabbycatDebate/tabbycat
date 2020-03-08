import logging

from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from participants.models import Institution, Team

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Institution)
def update_team_names_from_institution(sender, instance, created, **kwargs):
    teams = instance.team_set.all()
    if len(teams) > 0:
        logger.info("Updating names of all %d teams from institution %s" % (len(teams), instance.name))
        for team in teams:
            team.save()


@receiver(post_save, sender=Team)
def update_team_cache(sender, instance, created, **kwargs):
    cached_key = "%s_%s_%s" % ('teamid', instance.id, '_institution__object')
    cache.delete(cached_key)
    cached_key = "%s_%s_%s" % ('teamid', instance.id, '_speaker__objects')
    cache.delete(cached_key)
