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

    VIEW_ACTIONLOGENTRIES = 'view.actionlogentry', _("view action log entries")
    # EDIT_ACTIONLOGENTRIES omitted as pre-supposed when taking an action

    VIEW_TEAMS = 'view.team', _("view teams")
    ADD_TEAMS = 'add.team', _("add teams")

    VIEW_ROUNDAVAILABILITIES_TEAM = 'view.roundavailability.team', _("view round availabilities for teams")
    VIEW_ROUNDAVAILABILITIES_ADJ = 'view.roundavailability.adjudicator', _("view round availabilities for adjudicators")
    VIEW_ROUNDAVAILABILITIES_VENUE = 'view.roundavailability.venue', _("view round availabilities for rooms")
    EDIT_ROUNDAVAILABILITIES_TEAM = 'edit.roundavailability.team', _("edit round availabilities for teams")
    EDIT_ROUNDAVAILABILITIES_ADJ = 'edit.roundavailability.adjudicator', _("edit round availabilities for adjudicators")
    EDIT_ROUNDAVAILABILITIES_VENUE = 'edit.roundavailability.venue', _("edit round availabilities for rooms")

    VIEW_DEBATES = 'view.debate', _("view debates (draw)")
    VIEW_ADMIN_DRAW = 'view.debate.admin', _("view debates (detailed draw)")
    GENERATE_DEBATE = 'generate.debate', _("generate debates (draw)")
    EDIT_DEBATETEAMS = 'edit.debateteam', _("edit debate teams (pairings)")
    VIEW_DEBATEADJUDICATORS = 'view.debateadjudicator', _("view debate adjudicators (allocations)")
    EDIT_DEBATEADJUDICATORS = 'edit.debateadjudicator', _("edit debate adjudicators (allocations)")

    # Logic behind the ballotsub permissions:
    # Confirmed ballots are more prominent than old ones, but are more sensitive to changes.
    # Then, assistants may confirm others' ballots but not their own.
    VIEW_NEW_BALLOTSUBMISSIONS = 'view.ballotsubmission.new', _("view confirmed ballots")
    EDIT_OLD_BALLOTSUBMISSIONS = 'edit.ballotsubmission.old', _("edit non-confirmed ballots")
    VIEW_BALLOTSUBMISSIONS = 'view.ballotsubmission', _("view any ballot")
    EDIT_BALLOTSUBMISSIONS = 'edit.ballotsubmission', _("edit any ballot")
    ADD_BALLOTSUBMISSIONS = 'add.ballotsubmission', _("create ballots")
    MARK_BALLOTSUBMISSIONS = 'mark.ballotsubmission', _("confirm/discard any ballot")
    MARK_OTHERS_BALLOTSUBMISSIONS = 'mark.ballotsubmission.others', _("confirm/discard others' ballots")
    VIEW_BALLOTSUBMISSION_GRAPH = 'view.ballotsubmission.graph', _("view ballot graph")

    VIEW_TOURNAMENTPREFERENCEMODEL = 'view.tournamentpreferencemodel', _("view tournament configuration")
    EDIT_TOURNAMENTPREFERENCEMODEL = 'edit.tournamentpreferencemodel', _("edit tournament configuration")
