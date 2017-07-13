from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from breakqual.models import BreakCategory
from participants.models import Institution, Team

import logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Institution)
def update_team_names_from_institution(sender, instance, created, **kwargs):
    teams = instance.team_set.all()
    if len(teams) > 0:
        logger.info("Updating names of all %d teams from institution %s" % (len(teams), instance.name,))
        for team in teams:
            team.save()


@receiver(post_save, sender=Team)
def update_team_cache(sender, instance, created, **kwargs):
    cached_key = "%s_%s_%s" % ('teamid', instance.id, '_institution__object')
    cache.delete(cached_key)
    cached_key = "%s_%s_%s" % ('teamid', instance.id, '_speaker__objects')
    cache.delete(cached_key)

    try:
        t = instance.tournament
    except ObjectDoesNotExist:
        return # Loaded fixtures have no tournament_cache which crashes tests

    if created and instance.type not in (Team.TYPE_SWING, Team.TYPE_BYE):
        # Only add all is_general break categories to newly-created teams
        open_cats = BreakCategory.objects.filter(tournament=t, is_general=True)
        for cat in open_cats:
            logger.info("Auto-adding %s break category to %s" % (cat, instance))
            # Can't alter M2M fields in a post_save filter using add(); instead:
            transaction.on_commit(lambda: instance.break_categories.add(cat))
