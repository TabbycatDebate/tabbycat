from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.fields import ChoiceArrayField

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


class Group(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("name"))
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE, verbose_name=_("tournament"))
    permissions = ChoiceArrayField(blank=True, default=list,
        base_field=models.CharField(max_length=50, choices=Permission.choices), verbose_name=_("permissions"))

    class Meta:
        verbose_name = _("group")
        verbose_name_plural = _("groups")
        unique_together = [('name', 'tournament')]

    def __str__(self):
        return "%s (%s)" % (self.name, self.tournament.slug)


class Membership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, verbose_name=_("user"))
    group = models.ForeignKey(Group, models.CASCADE, verbose_name=_("group"))

    class Meta:
        verbose_name = _("group membership")
        verbose_name_plural = _("group memberships")
        unique_together = [('user', 'group')]
