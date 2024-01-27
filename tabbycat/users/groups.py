from typing import List, Optional

from django.utils.translation import gettext_lazy as _

from options.presets import _all_subclasses

from .permissions import Permission


def all_groups():
    yield from _all_subclasses(BaseGroup)


class BaseGroup:
    name: Optional[str] = None
    permissions: List[Permission] = []


class Equity(BaseGroup):
    # Permissions to manage conflicts/constraints, view feedback + participant info
    name = _("Equity")
    permissions = [
        Permission.EDIT_ROOMCATEGORIES,
        Permission.EDIT_ROOMCONSTRAINTS,
        Permission.EDIT_ADJ_ADJ_CONFLICTS,
        Permission.EDIT_ADJ_INST_CONFLICTS,
        Permission.EDIT_ADJ_INST_CONFLICTS,
        Permission.EDIT_TEAM_INST_CONFLICTS,
        Permission.VIEW_PARTICIPANTS,
        Permission.VIEW_TEAMS,
        Permission.VIEW_ADJUDICATORS,
        Permission.VIEW_ROOMS,
        Permission.VIEW_INSTITUTIONS,
    ]


class AdjudicationCore(BaseGroup):
    # Permissions to make [preformed] allocations, view feedback, and create motions
    name = _("Adjudication Core")
    permissions = [
        Permission.EDIT_BASEJUDGESCORES_IND,
        Permission.EDIT_DEBATEADJUDICATORS,
        Permission.EDIT_FEEDBACK_CONFIRM,
        Permission.EDIT_FEEDBACK_IGNORE,
        Permission.EDIT_FEEDBACK_OVERVIEW,
        Permission.EDIT_JUDGESCORES_BULK,
        Permission.EDIT_MOTION,
        Permission.EDIT_STARTTIME,
        Permission.EDIT_PREFORMEDPANELS,
        Permission.EDIT_RELEASEMOTION,
        Permission.EDIT_UNRELEASEMOTION,
        Permission.EDIT_ROOMALLOCATIONS,
        Permission.EDIT_ALLOCATESIDES,
        Permission.EDIT_ADJ_BREAK,
        Permission.VIEW_BREAK,
        Permission.VIEW_BREAK_OVERVIEW,
        Permission.VIEW_MOTIONSTAB,
        Permission.VIEW_DIVERSITYTAB,
        Permission.VIEW_STANDINGS_OVERVIEW,
        Permission.VIEW_TEAMSTANDINGS,
        Permission.VIEW_SPEAKERSSTANDINGS,
        Permission.VIEW_REPLIESSTANDINGS,
        Permission.VIEW_FEEDBACK,
        Permission.ADD_FEEDBACK,
        Permission.VIEW_PARTICIPANTS,
        Permission.VIEW_TEAMS,
        Permission.VIEW_ADJUDICATORS,
        Permission.VIEW_ROOMS,
        Permission.VIEW_INSTITUTIONS,
    ]


class TabDirector(BaseGroup):
    # All permissions
    name = _("Tabulation Director")
    permissions = [p for p in Permission]


class TabAssistant(BaseGroup):
    # Permissions to match the Assistant interface
    name = _("Tabulation Assistant")
    permissions = [
        Permission.EDIT_ROUNDAVAILABILITIES_ADJ,
        Permission.EDIT_ROUNDAVAILABILITIES_TEAM,
        Permission.EDIT_ROUNDAVAILABILITIES_VENUE,
        Permission.EDIT_ROOMCATEGORIES,
        Permission.EDIT_ROOMCONSTRAINTS,
        Permission.VIEW_ADMIN_DRAW,
        Permission.EDIT_OLD_BALLOTSUBMISSIONS,
        Permission.EDIT_BALLOTSUBMISSIONS,
        Permission.ADD_BALLOTSUBMISSIONS,
        Permission.MARK_BALLOTSUBMISSIONS,
        Permission.MARK_OTHERS_BALLOTSUBMISSIONS,
        Permission.VIEW_BALLOTSUBMISSION_GRAPH,
        Permission.VIEW_FEEDBACK,
        Permission.VIEW_FEEDBACK_OVERVIEW,
        Permission.VIEW_FEEDBACK_UNSUBMITTED,
        Permission.EDIT_FEEDBACK_CONFIRM,
        Permission.EDIT_FEEDBACK_IGNORE,
        Permission.ADD_FEEDBACK,
        Permission.EDIT_BREAK_ELIGIBILITY,
        Permission.EDIT_SPEAKER_CATEGORIES,
        Permission.VIEW_PRIVATE_URLS,
        Permission.GENERATE_PRIVATE_URLS,
        Permission.SEND_PRIVATE_URLS,
        Permission.EDIT_PARTICIPANT_CHECKIN,
        Permission.EDIT_ROOM_CHECKIN,
        Permission.VIEW_TEAMS,
        Permission.VIEW_ADJUDICATORS,
        Permission.VIEW_ROOMS,
        Permission.VIEW_INSTITUTIONS,
        Permission.VIEW_PARTICIPANTS,
        Permission.VIEW_ADMIN_DRAW,
        Permission.VIEW_DEBATES,
        Permission.RELEASE_DRAW,
        Permission.UNRELEASE_DRAW,
        Permission.EDIT_STARTTIME,
    ]


class Language(BaseGroup):
    name = _("Language")
    permissions = [
        Permission.EDIT_BREAK_ELIGIBILITY,
        Permission.EDIT_SPEAKER_CATEGORIES,
        Permission.VIEW_PARTICIPANTS,
        Permission.VIEW_TEAMS,
        Permission.VIEW_ADJUDICATORS,
        Permission.VIEW_ROOMS,
        Permission.VIEW_INSTITUTIONS,
    ]
