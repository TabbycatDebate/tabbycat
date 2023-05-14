from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .permissions import Permission


class UserPermission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, verbose_name=_("user"))
    permission = models.CharField(max_length=50, choices=Permission.choices, verbose_name=_("permission"))
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE, verbose_name=_("tournament"))

    class Meta:
        verbose_name = _("user permission")
        verbose_name_plural = _("user permissions")
        unique_together = [('user', 'permission', 'tournament')]

    def __str__(self):
        return "%s: %s (%s)" % (self.user.username, self.permission, self.tournament.slug)
