from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.fields import ChoiceArrayField
from utils.models import UniqueConstraint

from .permissions import PERM_CACHE_KEY, Permission


class UserPermission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, verbose_name=_("user"))
    permission = models.CharField(max_length=50, choices=Permission.choices, verbose_name=_("permission"))
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE, verbose_name=_("tournament"))

    class Meta:
        constraints = [UniqueConstraint(fields=['user', 'permission', 'tournament'])]
        verbose_name = _("user permission")
        verbose_name_plural = _("user permissions")

    def __str__(self):
        return "%s: %s (%s)" % (self.user.username, self.permission, self.tournament.slug)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.set(PERM_CACHE_KEY % (self.user_id, self.tournament.slug, str(self.permission)), True)

    def delete(self, *args, **kwargs):
        cache.delete(PERM_CACHE_KEY % (self.user_id, self.tournament.slug, str(self.permission)))
        return super().delete(*args, **kwargs)


class Group(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("name"))
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE, verbose_name=_("tournament"))
    permissions = ChoiceArrayField(blank=True, default=list,
        base_field=models.CharField(max_length=50, choices=Permission.choices), verbose_name=_("permissions"))
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership', related_name='group_set')

    class Meta:
        constraints = [UniqueConstraint(fields=['name', 'tournament'])]
        verbose_name = _("group")
        verbose_name_plural = _("groups")

    def __str__(self):
        return "%s (%s)" % (self.name, self.tournament.slug)


class Membership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, verbose_name=_("user"))
    group = models.ForeignKey(Group, models.CASCADE, verbose_name=_("group"))

    class Meta:
        constraints = [UniqueConstraint(fields=['user', 'group'])]
        verbose_name = _("group membership")
        verbose_name_plural = _("group memberships")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.set_many({PERM_CACHE_KEY % (self.user_id, self.group.tournament.slug, str(perm)): True for perm in self.group.permissions})

    def delete(self, *args, **kwargs):
        cache.delete_many([PERM_CACHE_KEY % (self.user_id, self.group.tournament.slug, str(perm)) for perm in self.group.permissions])
        return super().delete(*args, **kwargs)
