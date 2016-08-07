"""Module to compute the teams breaking in a BreakCategory."""

from standings.teams import TeamStandingsGenerator

import logging
logger = logging.getLogger(__name__)


def get_breaking_teams(category, include_all=False, include_categories=False):
    """Returns a list of Teams, with additional attributes. For each Team t in
    the returned list:
        t.rank is the rank of the team, including ineligible teams.
        t.break_rank is the rank of the team out of those that are in the break.
    'category' must be a BreakCategory instance.

    If 'include_all' is True:
      - Teams that would break but for the institution cap are included in the
        returned list, with t.break_rank set to the string "(capped)".
      - If category.is_general is True, then teams that would break but for
        being ineligible for this category are included in the returned list,
        but with t.break_rank set to the string "(ineligible)".
    Note that in no circumstances are teams that broke in a higher priority
    category included in the list of returned teams.

    If 'include_all' is False, the capped and ineligible teams are excluded,
    but t.rank is still the rank including those teams.

    If 'include_categories' is True, t.categories_for_display will be a comma-
    delimited list of category names that are not this category, and lower
    or equal priority to this category.
    """
    teams = category.breaking_teams.all()
    if not include_all:
        teams = teams.filter(break_rank__isnull=False)

    metrics = category.tournament.pref('team_standings_precedence')
    generator = TeamStandingsGenerator(metrics, ('rank',))
    standings = generator.generate(teams)

    for standing in standings:

        bt = standing.team.breakingteam_set.get(break_category=category)
        standing.rank = bt.rank
        if bt.break_rank is None:
            if bt.remark:
                standing.break_rank = "(" + bt.get_remark_display().lower() + ")"
            else:
                standing.break_rank = "<error>"
        else:
            standing.break_rank = bt.break_rank

        if include_categories:
            categories = standing.team.break_categories_nongeneral.exclude(id=category.id).exclude(priority__lt=category.priority)
            standing.categories_for_display = "(" + ", ".join(c.name for c in categories) + ")" if categories else ""
        else:
            standing.categories_for_display = ""

    return standings
