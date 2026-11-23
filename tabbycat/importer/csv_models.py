"""Models and names used by shared CSV reference fields."""

from django.db.models import Q

from adjallocation.models import (AdjudicatorAdjudicatorConflict, AdjudicatorInstitutionConflict,
                                  AdjudicatorTeamConflict, TeamInstitutionConflict)
from adjfeedback.models import AdjudicatorBaseScoreHistory, AdjudicatorFeedbackQuestion
from breakqual.models import BreakCategory
from draw.models import TeamSideAllocation
from motions.models import Motion
from participants.models import Adjudicator, Institution, Region, SpeakerCategory, Team
from tournaments.models import Round
from venues.models import Venue, VenueCategory, VenueConstraint


CSV_MODELS = {
    'region': Region, 'institution': Institution, 'venue_category': VenueCategory,
    'break_category': BreakCategory, 'speaker_category': SpeakerCategory, 'round': Round,
    'team': Team, 'adjudicator': Adjudicator, 'venue': Venue, 'motion': Motion,
    'adj_feedback_question': AdjudicatorFeedbackQuestion, 'score': AdjudicatorBaseScoreHistory,
    'team_conflict': AdjudicatorTeamConflict, 'institution_conflict': AdjudicatorInstitutionConflict,
    'adjudicator_conflict': AdjudicatorAdjudicatorConflict, 'team_institution_conflict': TeamInstitutionConflict,
    'side': TeamSideAllocation, 'adj_venue_constraint': VenueConstraint, 'team_venue_constraint': VenueConstraint,
}
NAME_FIELDS = {
    'institution': ('name', 'code'), 'team': ('reference', 'short_name', 'long_name'),
    'round': ('abbreviation', 'name', 'seq'), 'motion': ('reference',),
    'break_category': ('slug', 'name'), 'speaker_category': ('slug', 'name'),
}
IMPLICIT_REFERENCE_TYPES = ('region', 'venue_category')


def csv_queryset(kind, tournament):
    model = CSV_MODELS[kind]
    manager = model.objects
    queryset = getattr(manager, 'all_with_unconfirmed', manager.all())
    if kind == 'adjudicator':
        return queryset.filter(Q(tournament=tournament) | Q(tournament__isnull=True))
    if any(field.name == 'tournament' for field in model._meta.fields):
        queryset = queryset.filter(tournament=tournament)
    if kind == 'team':
        queryset = queryset.select_related('institution')
    return queryset
