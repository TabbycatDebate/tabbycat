from itertools import groupby
from typing import List, TYPE_CHECKING, Union

from django.core.cache import cache
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from django.conf import settings
    from tournaments.models import Tournament

PERM_CACHE_KEY = "user_%d_%s_%s_permission"


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
    VIEW_DECODED_TEAMS = 'view.teamname', _("view decoded team names")
    VIEW_ANONYMOUS = 'view.anonymous', _("View names of anonymized participants")
    VIEW_ADJUDICATORS = 'view.adj', _("view adjudicators")
    ADD_ADJUDICATORS = 'add.adj', _("add adjudicators")
    VIEW_ROOMS = 'view.room', _("view rooms")
    ADD_ROOMS = 'add.room', _("add rooms")
    VIEW_INSTITUTIONS = 'view.inst', _("view institutions")
    ADD_INSTITUTIONS = 'add.inst', _("add institutions")
    VIEW_PARTICIPANTS = 'view.particpants', _("view participants")
    VIEW_PARTICIPANT_GENDER = 'view.participants.gender', _("view participants' gender information")
    VIEW_PARTICIPANT_CONTACT = 'view.participants.contact', _("view participants' contact information")
    VIEW_PARTICIPANT_DECODED = 'view.participants.decoded', _("view participants' real names")
    VIEW_PARTICIPANT_INST = 'view.participants.inst', _("view participants' institution")

    VIEW_ROUNDAVAILABILITIES_TEAM = 'view.roundavailability.team', _("view round availabilities for teams")
    VIEW_ROUNDAVAILABILITIES_ADJ = 'view.roundavailability.adjudicator', _("view round availabilities for adjudicators")
    VIEW_ROUNDAVAILABILITIES_VENUE = 'view.roundavailability.venue', _("view round availabilities for rooms")
    EDIT_ROUNDAVAILABILITIES_TEAM = 'edit.roundavailability.team', _("edit round availabilities for teams")
    EDIT_ROUNDAVAILABILITIES_ADJ = 'edit.roundavailability.adjudicator', _("edit round availabilities for adjudicators")
    EDIT_ROUNDAVAILABILITIES_VENUE = 'edit.roundavailability.venue', _("edit round availabilities for rooms")
    VIEW_ROUNDAVAILABILITIES = 'view.roundavailability', _("view round availabilities")
    EDIT_ROUNDAVAILABILITIES = 'edit.roundavailability', _("edit round availabilities")

    VIEW_ROOMCONSTRAINTS = 'view.roomconstraints', _("view room constraints")
    VIEW_ROOMCATEGORIES = 'view.roomcategories', _("view room categories")
    EDIT_ROOMCONSTRAINTS = 'edit.roomconstraints', _("edit room constraints")
    EDIT_ROOMCATEGORIES = 'edit.roomcategories', _("edit room categories")

    VIEW_DEBATE = 'view.debate', _("view debates (draw)")
    VIEW_ADMIN_DRAW = 'view.debate.admin', _("view debates (detailed draw)")
    GENERATE_DEBATE = 'generate.debate', _("generate debates (draw)")
    EDIT_DEBATETEAMS = 'edit.debateteam', _("edit debate teams (pairings)")
    VIEW_DEBATEADJUDICATORS = 'view.debateadjudicator', _("view debate adjudicators (allocations)")
    EDIT_DEBATEADJUDICATORS = 'edit.debateadjudicator', _("edit debate adjudicators (allocations)")
    VIEW_ROOMALLOCATIONS = 'view.roomallocations', _("view room allocations")
    EDIT_ROOMALLOCATIONS = 'edit.roomallocations', _("edit room allocations")
    EDIT_ALLOCATESIDES = 'edit.allocatesides', _("edit and confirm outround team positions")

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
    VIEW_RESULTS = 'view.results', _("view results entry page")

    VIEW_MOTION = 'view.roundmotion', _("view motion per round")
    EDIT_MOTION = 'edit.roundmotion', _("edit motion per round")
    RELEASE_DRAW = 'release.draw', _("release draw to public")
    RELEASE_MOTION = 'release.motion', _("release motion to public")
    UNRELEASE_DRAW = 'unrelease.draw', _("unrelease draw to public")
    UNRELEASE_MOTION = 'unrelease.motion', _("unrelease motion to public")
    EDIT_STARTTIME = 'edit.starttime', _("add debate start time")
    VIEW_DRAW = 'view.draw', _("view draws")

    VIEW_BRIEFING_DRAW = 'view.briefingdraw', _("view draws (for the briefing room)")
    DISPLAY_MOTION = 'display.motion', _("display motion (for the briefing room)")

    VIEW_TOURNAMENTPREFERENCEMODEL = 'view.tournamentpreferencemodel', _("view tournament configuration")
    EDIT_TOURNAMENTPREFERENCEMODEL = 'edit.tournamentpreferencemodel', _("edit tournament configuration")

    VIEW_PREFORMEDPANELS = 'view.preformedpanels', _("view existing preformed panels")
    EDIT_PREFORMEDPANELS = 'edit.preformedpanels', _("edit preformed panels")

    # standings tab
    VIEW_STANDINGS_OVERVIEW = 'view.standingsoverview', _("view the overviews of standings")
    VIEW_TEAMSTANDINGS = 'view.teamstandings', _("view the most recent team standings")
    VIEW_SPEAKERSSTANDINGS = 'view.speakersstandings', _("view the most recent speaker standings")
    VIEW_REPLIESSTANDINGS = 'view.repliesstandings', _("view the most recent replies standings")
    VIEW_MOTIONSTAB = 'view.motionstab', _("view the most recent motions tab")
    VIEW_DIVERSITYTAB = 'view.diversitytab', _("view the diversity tab")

    # Feedback tab
    VIEW_FEEDBACK_OVERVIEW = 'view.feedbackoverview', _("view overview of judge feedback")
    EDIT_JUDGESCORES_BULK = 'edit.judgescoresbulk', _("bulk update judge scores")
    EDIT_BASEJUDGESCORES_IND = 'edit.judgescoresind', _("edit base scores of judges")
    VIEW_FEEDBACK = 'view.feedback', _("view feedback")
    EDIT_FEEDBACK_IGNORE = 'edit.feedbackignore', _("toggle ignore feedback")
    EDIT_FEEDBACK_CONFIRM = 'edit.feedbackconfirm', _("toggle confirm feedback")
    VIEW_FEEDBACK_UNSUBMITTED = 'view.feedbackunsubmitted', _("view feedback unsubmitted tab")
    ADD_FEEDBACK = 'add.feedback', _("add feedback")
    VIEW_ADJ_BREAK = 'view.adj.break', _("view adjudicator break")
    EDIT_ADJ_BREAK = 'edit.adj.break', _("edit adjudicator break")
    # idk if its possible for them to add feedback everywhere, considering there is add feedback on multiple pages

    EDIT_FEEDBACKQUESTION = 'edit.feedbackquestion', _("edit feedback questions")

    # breaks
    EDIT_BREAK_ELIGIBILITY = 'edit.breakeligibility', _("edit break eligibility")
    VIEW_BREAK_ELIGIBILITY = 'view.breakeligibility', _("view break eligibility")
    EDIT_BREAK_CATEGORIES = 'edit.breakcategories', _("edit break categories")
    VIEW_BREAK_CATEGORIES = 'view.breakcategories', _("view break categories")
    VIEW_SPEAKER_CATEGORIES = 'view.speakercategories', _("view speaker categories")
    EDIT_SPEAKER_CATEGORIES = 'edit.speakercategories', _("edit speaker categories")
    VIEW_SPEAKER_ELIGIBILITY = 'view.speakereligibility', _("view speaker eligibility")
    EDIT_SPEAKER_ELIGIBILITY = 'edit.speakereligibility', _("edit speaker eligibility")
    VIEW_BREAK_OVERVIEW = 'view.break.overview', _("view break overview")
    VIEW_BREAK = 'view.break', _("view breaks")
    GENERATE_BREAK = 'generate.break', _("generate all breaks")

    VIEW_PRIVATE_URLS = 'view.privateurls', _("view private urls")
    VIEW_PRIVATE_URLS_EMAIL_LIST = 'view.privateurls.emaillist', _("view private urls email list")
    GENERATE_PRIVATE_URLS = 'generate.privateurls', _("generate private URLs")
    # need to get rid of generate private urls soons
    SEND_PRIVATE_URLS = 'send.privateurls', _("send private URLs")

    VIEW_CHECKIN = 'view.checkin', _("view checkins")
    EDIT_PARTICIPANT_CHECKIN = 'edit.participantcheckin', _("edit participant check-in")
    EDIT_ROOM_CHECKIN = 'edit.roomcheckin', _("edit room check-in")

    EDIT_ROUND = 'edit.round', _("edit round attributes")
    DELETE_ROUND = 'delete.round', _("delete rounds")
    CREATE_ROUND = 'add.round', _("create rounds")

    VIEW_EMAIL_STATUSES = 'view.emails', _("view email statuses")
    SEND_EMAILS = 'send.emails', _("send participants email messages")

    EXPORT_XML = 'export.xml', _("export DebateXML")

    VIEW_SETTINGS = 'view.settings', _("view settings")
    EDIT_SETTINGS = 'edit.settings', _("edit settings")


permission_type = Union[Permission, bool]


def has_permission(user: 'settings.AUTH_USER_MODEL', permission: permission_type, tournament: 'Tournament') -> bool:
    if user.is_anonymous:
        return False
    if user.is_superuser:
        return True

    if isinstance(permission, bool):
        return permission

    if not hasattr(user, '_permissions'):
        user._permissions = {}

    if tournament.slug in user._permissions:
        if permission in user._permissions[tournament.slug]:
            return True
    else:
        user._permissions[tournament.slug] = set()

    cached_perm = cache.get(PERM_CACHE_KEY % (user.pk, tournament.slug, str(permission)))
    if cached_perm is not None:
        if cached_perm:
            user._permissions[tournament.slug].add(permission)
        return cached_perm

    perm = (
        user.userpermission_set.filter(permission=permission, tournament=tournament).exists() or
        user.membership_set.filter(group__permissions__contains=[permission], group__tournament=tournament).exists()
    )
    if perm:
        user._permissions[tournament.slug].add(permission)
        cache.set(PERM_CACHE_KEY % (user.pk, tournament.slug, str(permission)), perm)
    return perm


def get_permissions(user: 'settings.AUTH_USER_MODEL') -> List['Tournament']:
    user_perms = {}
    for t, groups in groupby(user.membership_set.select_related('group', 'group__tournament').order_by('group__tournament').all(), key=lambda m: m.group.tournament):
        tournament = user_perms.setdefault(t.id, t)
        tournament.permissions = set()
        tournament.groups = [m.group for m in groups]
        for g in tournament.groups:
            tournament.permissions |= set(g.permissions)
    for t, perms in groupby(user.userpermission_set.select_related('tournament').order_by('tournament').all(), key=lambda p: p.tournament):
        tournament = user_perms.setdefault(t.id, t)
        tournament.permissions = getattr(tournament, 'permissions', set()) | {p.permission for p in perms}

    return list(user_perms.values())
