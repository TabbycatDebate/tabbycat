"""Module to compute the teams breaking in a BreakCategory."""

from collections import Counter
from standings import annotate_team_standings

def compute_breaking_teams(category, include_all=False):
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

    If 'include_all' is False, t.rank == t.break_rank for every t in the returned list.
    """
    higher_breaking_teams = _compute_higher_priority_breaks(category)
    if category.is_general:
        eligible_teams = category.tournament.team_set # all in tournament
    else:
        eligible_teams = category.team_set
    eligible_teams = eligible_teams.exclude(pk__in=[t.pk for t in higher_breaking_teams])
    return _compute_breaking_teams(category, eligible_teams, include_all=include_all)

def _compute_higher_priority_breaks(category):
    higher_categories = category.tournament.breakcategory_set.filter(priority__lt=category.priority).order_by('priority')

    teams_broken_higher_priority = set()
    teams_broken_cur_priority = set()
    cur_priority = None
    for higher_category in higher_categories:

        # If this is a new priority level, reset the current list
        if cur_priority != higher_category.priority:
            teams_broken_higher_priority |= teams_broken_cur_priority
            teams_broken_cur_priority = set()
            cur_priority = higher_category.priority

        eligible_teams = higher_category.team_set.exclude(pk__in=[t.pk for t in teams_broken_higher_priority])
        this_break = _compute_breaking_teams(higher_category, eligible_teams)
        teams_broken_cur_priority.update(this_break)

    return teams_broken_higher_priority | teams_broken_cur_priority

def _compute_breaking_teams(category, eligible_teams, include_all=False):
    """Returns a list of Teams with annotations conforming to that described in
    the docstring of compute_breaking_teams."""

    eligible_teams = annotate_team_standings(eligible_teams, tournament=category.tournament)

    break_size = category.break_size
    institution_cap = category.institution_cap

    prev_rank_value = (None, None) # (points, speaks)
    cur_rank = 0
    breaking_teams = list()

    # Variables for institutional caps and non-breaking teams
    cur_break_rank = 0 # actual break rank
    cur_break_seq = 0  # sequential count of breaking teams
    teams_from_institution = Counter()

    for i, team in enumerate(eligible_teams, start=1):

        # Compute overall rank
        rank_value = (team.points, team.speaker_score)
        is_new_rank = rank_value != prev_rank_value
        if is_new_rank:
            # if we were up to the last break rank and this would be a new one, we're done
            if cur_break_rank == break_size:
                break
            cur_rank = i
            prev_rank_value = rank_value
        team.rank = cur_rank

        # Check if ineligible
        if not team.break_categories.filter(pk=category.pk).exists():
            team.break_rank = "(ineligible)"
            if include_all:
                breaking_teams.append(team)

        # Check if capped out by institution cap
        elif institution_cap > 0 and teams_from_institution[team.institution] >= institution_cap:
            team.break_rank = "(capped)"
            if include_all:
                breaking_teams.append(team)

        # If neither, this team is in the break
        else:
            # Compute break rank
            cur_break_seq += 1
            if is_new_rank:
                cur_break_rank = cur_break_seq
            team.break_rank = cur_break_rank
            breaking_teams.append(team)

        if cur_break_rank > break_size:
            break

        # Take note of the institution
        teams_from_institution[team.institution] += 1


    return breaking_teams