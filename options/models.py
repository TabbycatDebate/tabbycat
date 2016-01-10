from django.db import models
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from tournaments.models import Tournament
from dynamic_preferences.models import PerInstancePreferenceModel

class OptionManager(models.Manager):

    def set(self, tournament, key, value):
        obj, created = self.get_or_create(tournament=tournament, key=key)
        obj.value = value
        obj.save()
        #print "set config cache via set() call"
        cached_key = "%s_%s" % (tournament.slug, key)
        cache.set(cached_key, value, None)

    def get_(self, tournament, key, default=None):
        cached_key = "%s_%s" % (tournament.slug, key)
        cached_value = cache.get(cached_key)
        if cached_value:
            return cached_value
        else:
            #print "couldnt get cache key %s" % cached_key
            #print "\t value is %s" % cache.get(cached_key)
            try:
                noncached_value = self.get(tournament=tournament, key=key).value
            except ObjectDoesNotExist:
                noncached_value = default

            cache.set(cached_key, noncached_value, None)
            #print "\tset config cache %s to %s via get() call" % (cached_key, noncached_value)
            return noncached_value


class Option(models.Model):
    tournament = models.ForeignKey('tournaments.Tournament')
    key = models.CharField(max_length=40)
    value = models.CharField(max_length=40)

    objects = OptionManager()


class TournamentPreferenceModel(PerInstancePreferenceModel):

    instance = models.ForeignKey(Tournament)

    class Meta(PerInstancePreferenceModel.Meta):
        app_label = 'dynamic_preferences' # Can't change this
        verbose_name = "Tournament Preference"
        verbose_name_plural = "Tournament Preferencess"
