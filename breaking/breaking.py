"""Module to compute the teams breaking in a BreakCategory."""

from collections import Counter
from standings.standings import annotate_team_standings

from . import models

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

        if include_categories:
            categories = team.break_categories_nongeneral.exclude(id=category.id).exclude(priority__lt=category.priority)
            team.categories_for_display = "(" + ", ".join(c.name for c in categories) + ")" if categories else ""
        else:
            team.categories_for_display = ""

    return teams

def generate_all_breaking_teams(tournament):
    """Deletes all breaking teams information, then generates breaking teams
    from scratch according to update_breaking_teams()."""
    for category in tournament.breakcategory_set.all():
        category.breakingteam_set.all().delete()
    update_all_breaking_teams(tournament)

def update_all_breaking_teams(tournament):
    """Runs update_breaking_teams for all categories, taking taking break
    category priorities into account appropriately.
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

        eligible_teams = _eligible_team_set(category)
        this_break = _generate_breaking_teams(category, eligible_teams, teams_broken_higher_priority)
        teams_broken_cur_priority.update(this_break)

def update_breaking_teams(category):
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
            - BreakingTeam.REMARK_DIFFERENT_BREAK if the team broke in a
              different category.

    If a breaking team entry already exists and there is a remark associated
    with it, it retains the remark and skips that team.
    """
    higher_breakingteams = models.BreakingTeam.objects.filter(break_category__priority__lt=category.priority, break_rank__isnull=False).select_related('team')
    higher_teams = {bt.team for bt in higher_breakingteams}
    eligible_teams = _eligible_team_set(category)
    _generate_breaking_teams(category, eligible_teams, higher_teams)

def _eligible_team_set(category):
    if category.is_general:
        return category.tournament.team_set # all in tournament
    else:
        return category.team_set

def _generate_breaking_teams(category, eligible_teams, teams_broken_higher_priority=set()):
    """Generates a list of breaking teams for the given category and returns
    a list of teams in the (actual) break, i.e. excluding teams that are
    ineligible, capped, broke in a different break, and so on."""

    eligible_teams = annotate_team_standings(eligible_teams, tournament=category.tournament)

    break_size = category.break_size
    institution_cap = category.institution_cap

    prev_rank_value = (None, None) # (points, speaks)
    cur_rank = 0
    breaking_teams = list()
    breaking_teams_to_create = list()

    # Variables for institutional caps and non-breaking teams
    cur_break_rank = 0 # actual break rank
    cur_break_seq = 0  # sequential count of breaking teams
    teams_from_institution = Counter()

    for i, team in enumerate(eligible_teams, start=1):

        try:
            bt = models.BreakingTeam.objects.get(break_category=category, team=team)
            existing = True
        except models.BreakingTeam.DoesNotExist:
            bt = models.BreakingTeam(break_category=category, team=team)
            existing = False

        # Compute overall rank
        rank_value = (team.points, team.speaker_score)
        is_new_rank = rank_value != prev_rank_value
        if is_new_rank:
            # if we have enough teams, we're done
            if len(breaking_teams) >= break_size:
                break
            cur_rank = i
            prev_rank_value = rank_value
        bt.rank = cur_rank

        # If there is an existing remark, scrub the break rank and skip
        if existing and bt.remark:
            bt.break_rank = None

        # Check if ineligible
        elif not team.break_categories.filter(pk=category.pk).exists():
            bt.remark = bt.REMARK_INELIGIBLE

        # Check if capped out by institution cap
        elif institution_cap > 0 and teams_from_institution[team.institution] >= institution_cap:
            bt.remark = bt.REMARK_CAPPED

        # Check if already broken to a higher category
        elif team in teams_broken_higher_priority:
            bt.remark = bt.REMARK_DIFFERENT_BREAK

        # If neither, this team is in the break
        else:
            # Compute break rank
            cur_break_seq += 1
            if is_new_rank:
                cur_break_rank = cur_break_seq
            bt.break_rank = cur_break_rank

            breaking_teams.append(team)

        bt.full_clean()
        if existing:
            bt.save()
        else:
            breaking_teams_to_create.append(bt)

        # Take note of the institution
        teams_from_institution[team.institution] += 1

    models.BreakingTeam.objects.bulk_create(breaking_teams_to_create)
    models.BreakingTeam.objects.filter(break_category=category, break_rank__isnull=False).exclude(
        team_id__in=[t.id for t in breaking_teams]).delete()


    return breaking_teams