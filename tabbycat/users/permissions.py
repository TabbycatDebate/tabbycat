from django.core.cache import cache
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


def has_permission(user, permission, tournament):
    if user.is_superuser:
        return True

    if isinstance(permission, bool):
        return permission

    if not hasattr(user, '_permissions'):
        user._permissions = {}

    if tournament.slug in user._permissions:
        return permission in user._permissions[tournament.slug]
    else:
        user._permissions[tournament.slug] = set()

    cached_perm = cache.get("user_%d_%s_%s_permission" % (user.pk, tournament.slug, str(permission)))
    if cached_perm is not None:
        if cached_perm:
            user._permissions[tournament.slug].add(permission)
        return cached_perm

    perm = user.userpermission_set.filter(permission=permission, tournament=tournament).exists()
    cache.set("user_%d_%s_%s_permission" % (user.pk, tournament.slug, str(permission)), perm)
    if perm:
        user._permissions[tournament.slug].add(permission)
    return perm


class Permission(TextChoices):
    VIEW_ADJ_TEAM_CONFLICTS = 'view.adjudicatorteamconflict', _("view adjudicator-team conflicts")
    EDIT_ADJ_TEAM_CONFLICTS = 'edit.adjudicatorteamconflict', _("edit adjudicator-team conflicts")
    VIEW_ADJ_ADJ_CONFLICTS = 'view.adjudicatoradjudicatorconflict', _("view adjudicator-adjudicator conflicts")
    EDIT_ADJ_ADJ_CONFLICTS = 'edit.adjudicatoradjudicatorconflict', _("edit adjudicator-adjudicator conflicts")
    VIEW_ADJ_INST_CONFLICTS = 'view.adjudicatorinstitutionconflict', _("view adjudicator-institution conflicts")
    EDIT_ADJ_INST_CONFLICTS = 'edit.adjudicatorinstitutionconflict', _("edit adjudicator-institution conflicts")
    VIEW_TEAM_INST_CONFLICTS = 'view.teaminstitutionconflict', _("view team-institution conflicts")
    EDIT_TEAM_INST_CONFLICTS = 'edit.teaminstitutionconflict', _("edit team-institution conflicts")
