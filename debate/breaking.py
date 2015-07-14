"""Module to compute the teams breaking in a BreakCategory."""

from collections import Counter
from standings import annotate_team_standings
from models import BreakingTeam

def get_breaking_teams(category, include_all=False):
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
    """
    teams = category.breaking_teams.all()
    if not include_all:
        teams = teams.filter(break_rank__isnull=False)
    teams = annotate_team_standings(teams, tournament=category.tournament)
    for team in teams:
        bt = team.breakingteam_set.get(break_category=category)
        team.rank = bt.rank
        if bt.break_rank is None:
            if bt.remark:
                team.break_rank = "(" + bt.get_remark_display().lower() + ")"
            else:
                team.break_rank = "<error>"
        else:
            team.break_rank = bt.break_rank
    return teams

def generate_breaking_teams(tournament):
    """Computes the breaking teams and stores them in the database as
    BreakingTeam objects. Each BreakingTeam bt has:
        bt.rank set to the rank of the team, including ineligible teams
        bt.break_rank set to the rank of the team out of those that are in the
            break, or None if the team is ineligible
        bt.remark set to
            - BreakingTeam.REMARK_CAPPED if the team would break but for the
              institution cap, or
            - BreakingTeam.REMARK_INELIGIBLE if category.is_general is True and
              the team would break but for being ineligible for this category.
    """
    teams_broken_higher_priority = set()
    teams_broken_cur_priority = set()
    cur_priority = None

    for category in tournament.breakcategory_set.order_by('priority'):

        # If this is a new priority level, reset the current list
        if cur_priority != category.priority:
            teams_broken_higher_priority |= teams_broken_cur_priority
            teams_broken_cur_priority = set()
            cur_priority = category.priority

        if category.is_general:
            eligible_teams = category.tournament.team_set # all in tournament
        else:
            eligible_teams = category.team_set
        eligible_teams = eligible_teams.exclude(pk__in=[t.pk for t in teams_broken_higher_priority])
        print category.name, eligible_teams.count()

        this_break = _generate_breaking_teams(category, eligible_teams)

        teams_broken_cur_priority.update(this_break)

def _generate_breaking_teams(category, eligible_teams):
    """Generates a list of breaking teams for the given category and returns it."""

    category.breaking_teams.all().delete()

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

        bt = BreakingTeam(break_category=category, team=team)

        # Compute overall rank
        rank_value = (team.points, team.speaker_score)
        is_new_rank = rank_value != prev_rank_value
        if is_new_rank:
            # if we were up to the last break rank and this would be a new one, we're done
            if cur_break_rank == break_size:
                break
            cur_rank = i
            prev_rank_value = rank_value
        bt.rank = cur_rank

        # Check if ineligible
        if not team.break_categories.filter(pk=category.pk).exists():
            bt.remark = bt.REMARK_INELIGIBLE

        # Check if capped out by institution cap
        elif institution_cap > 0 and teams_from_institution[team.institution] >= institution_cap:
            bt.remark = bt.REMARK_CAPPED

        # If neither, this team is in the break
        else:
            # Compute break rank
            cur_break_seq += 1
            if is_new_rank:
                cur_break_rank = cur_break_seq
            bt.break_rank = cur_break_rank

        bt.full_clean()
        bt.save()
        breaking_teams.append(team)

        if cur_break_rank > break_size:
            break

        # Take note of the institution
        teams_from_institution[team.institution] += 1

    return breaking_teams