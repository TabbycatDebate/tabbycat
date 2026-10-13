"""Participant setup shared by the CSV wizard and tournament importers."""

from adjallocation.models import TeamInstitutionConflict
from participants.emoji import set_emoji
from participants.models import Team

TEAM_SHORT_REFERENCE_LENGTH = Team._meta.get_field('short_reference').max_length


def team_reference(reference):
    return reference[:TEAM_SHORT_REFERENCE_LENGTH]


def initialize_teams(teams, tournament, *, general_break_categories=False):
    """Initialize newly saved teams in a batch, returning their own conflicts.

    Command importers keep their own category mappings; web imports opt into
    the general categories. Existing teams must not be passed to this function.
    """
    teams = list(teams)
    if not teams:
        return []
    set_emoji(teams, tournament)
    conflicts = [TeamInstitutionConflict(team=team, institution_id=team.institution_id)
        for team in teams if team.institution_id is not None]
    TeamInstitutionConflict.objects.bulk_create(conflicts)
    if general_break_categories:
        categories = list(tournament.breakcategory_set.filter(is_general=True))
        for team in teams:
            team.break_categories.set(categories)
    return conflicts
