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

    VIEW_MOTION = 'view.roundmotion', _("view motion per round")
    EDIT_MOTION = 'edit.roundmotion', _("edit motion per round")
    EDIT_RELEASEDRAW = 'edit.releasedraw', _("release draw to public")
    EDIT_RELEASEMOTION = 'edit.releasemotion', _("release motion to public")
    EDIT_STARTTIME = 'edit.starttime', _("add debate start time")
    # these permissions are already assigned to the assistants
    VIEW_ALLCURRENTDRAWS_ROOM = 'view.allcurrentdrawsroom', _("view all current draws by room")
    VIEW_ALLCURRENTDRAWS_TEAM = 'view.allcurrentdrawsteam', _("view all current draws by team")
    VIEW_ROUNDDRAW_ROOM = 'view.rounddrawroom', _("view current round draw by room")
    VIEW_ROUNDDRAW_TEAM = 'view.rounddrawteam', _("view current round draw by team")
    VIEW_DISPLAYMOTION = 'view.displaymotion', _("view display room motion page")

    VIEW_TOURNAMENTPREFERENCEMODEL = 'view.tournamentpreferencemodel', _("view tournament configuration")
    EDIT_TOURNAMENTPREFERENCEMODEL = 'edit.tournamentpreferencemodel', _("edit tournament configuration")

    VIEW_PREFORMEDPANELS = 'view.preformedpanels', _("view existing preformed panels")
    EDIT_PREFORMEDPANELS = 'edit.preformedpanels', _("edit existing preformed panels")

    # standings tab
    VIEW_STANDINGS_OVERVIEW = 'view.standingsoverview', _("view the overviews of standings")
    VIEW_TEAMSTANDINGS = 'view.teamstandings', _("view the most recent team standings")
    VIEW_SPEAKERSSTANDINGS = 'view.speakersstandings', _("view the most recent speaker standings")
    VIEW_REPLIESSTANDINGS = 'view.repliesstandings', _("view the most recent replies standings")
    VIEW_MOTIONSTAB = 'view.motionstab', _("view the most recent motions tab")
    VIEW_DIVERSITYTAB = 'view.diversitytab', _("view the diversity tab")

    # Feedback tab
    VIEW_FEEDBACK_OVERVIEW = 'view.feedbackoverview', _("view overview of judge feedback scores")
    EDIT_FEEDBACK_OVERVIEW = 'edit.feedbackoverview', _("edit overview of judge feedback scores")
    # not sure what the right most column of the overview page is called, but I'm calling it comments for now
    EDIT_JUDGESCORES_BULK = 'edit.judgescoresbulk', _("bulk update judge scores")
    EDIT_BASEJUDGESCORES_IND = 'edit.judgescoresind', _("edit base scores of judges")
    EDIT_SETBREAKING = 'edit.setbreaking', _("edit breaking judges")
    VIEW_FEEDBACK_LATEST = 'view.feedbacklatest', _("view the latest feedback tab")
    VIEW_FEEDBACK_IMPORTANT = 'view.feedbackimportant', _("view the important feedback tab")
    VIEW_FEEDBACK_COMMENTS = 'view.feedbackcomments', _("view the comments feedback tab")
    VIEW_FEEDBACK_BYSOURCE = 'view.feedbackbysource', _("view feedback by source")
    VIEW_FEEDBACK_BYTARGET = 'view.feedbackbytarget', _("view feedback by target")
    EDIT_FEEDBACK_IGNORE = 'edit.feedbackignore', _("edit the ignore feedback feature")
    EDIT_FEEDBACK_UNCONFIRM = 'edit.feedbackunconfirm', _("edit the unconfirm feedback feature")
    VIEW_FEEDBACK_UNSUBMITTED = 'view.feedbackunsubmitted', _("view feedback unsubmitted tab")
    VIEW_FEEDBACK_ADD = 'view.feedbackadd', _("view add feedback tab")
    EDIT_FEEDBACK_ADD = 'edit.feedbackadd', _("edit add feedback tab")
    # idk if its possible for them to add feedback everywhere, considering there is add feedback on multiple pages

    # breaks
    EDIT_BREAK_ELIGIBILITY = 'edit.breakeligibility', _("edit break eligibility")
    VIEW_BREAK_ELIGIBILITY = 'view.breakeligibility', _("view break eligibility")
    EDIT_BREAK_CATEGORIES = 'edit.breakcategories', _("edit break categories")
    VIEW_BREAK_CATEGORIES = 'view.breakcategories', _("view break categories")
    GENERATE_BREAK = 'generate.break', _("generate all breaks")
    EDIT_BREAK_REMARKS = 'edit.breakremarks', _("edit break remarks")
