"""Module to compute the teams breaking in a BreakCategory."""

from collections import Counter
from itertools import groupby
import logging
logger = logging.getLogger(__name__)

from standings.teams import TeamStandingsGenerator

from .models import BreakingTeam

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

        relevant_teams = _relevant_team_set(category)
        this_break = _generate_breaking_teams(category, relevant_teams, teams_broken_higher_priority)
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
    higher_breakingteams = BreakingTeam.objects.filter(break_category__priority__lt=category.priority, break_rank__isnull=False).select_related('team')
    higher_teams = {bt.team for bt in higher_breakingteams}
    relevant_teams = _relevant_team_set(category)
    _generate_breaking_teams(category, relevant_teams, higher_teams)

def _relevant_team_set(category):
    if category.is_general:
        return category.tournament.team_set.all() # all in tournament
    else:
        return category.team_set.all()

def _generate_breaking_teams(category, relevant_teams, teams_broken_higher_priority=set()):
    if category.rule == category.BREAK_QUALIFICATION_RULE_AIDA_2016:
        return _generate_breaking_teams_2016(category, relevant_teams, teams_broken_higher_priority)
    else:
        return _generate_breaking_teams_pre_2015(category, relevant_teams, teams_broken_higher_priority)

def _generate_breaking_teams_2016(category, teams, teams_broken_higher_priority=set()):
    """Generates a list of breaking teams for the given category and returns
    a list of teams in the (actual) break, i.e. excluding teams that are
    ineligible, capped, broke in a different break, and so on."""

    break_size = category.break_size
    institution_cap = category.institution_cap
    assert category.rule == category.BREAK_QUALIFICATION_RULE_AIDA_2016

    # Steps as laid out in proposed AIDA constitutional amendment
    # i. Generate standings
    metrics = category.tournament.pref('team_standings_precedence')
    assert "wins" in metrics, "Teams must be ranked by number of wins to use AIDA 2016 rule"
    generator = TeamStandingsGenerator(metrics, ('rank', 'institution'))
    generated = generator.generate(teams)
    standings = list(generated) # list of TeamStandingInfo objects

    # Discard ineligible teams
    existing_remark = []
    for tsi in standings:
        try:
            if BreakingTeam.objects.get(break_category=category, team=tsi.team).remark:
                existing_remark.append(tsi)
        except BreakingTeam.DoesNotExist:
            pass
    ineligible = [tsi for tsi in standings if not tsi.team.break_categories.filter(pk=category.pk).exists()]
    different_break = [tsi for tsi in standings if tsi.team in teams_broken_higher_priority]
    eligible = [tsi for tsi in standings if tsi not in existing_remark + ineligible + different_break]

    logger.info("Has existing remark: %s", existing_remark)
    logger.info("Ineligible to break: %s", ineligible)
    logger.info("In different break: %s", different_break)

    # ii. Discard teams with fewer wins than the nth ranked team
    # `effective_break_size` is the break size including ineligible teams
    if len(eligible) >= break_size:
        min_wins = eligible[break_size-1].metrics["wins"]
        eligible = [tsi for tsi in eligible if tsi.metrics["wins"] >= min_wins]
        effective_break_size = eligible[break_size-1].get_ranking("rank")
    else:
        effective_break_size = len(eligible)

    logger.info("Effective break size: %s", effective_break_size)

    # iii. Set aside teams that are capped out
    capped = []
    for tsi in eligible:
        if tsi.get_ranking("institution") > category.institution_cap:
            capped.append(tsi)
        elif tsi.get_ranking("institution") > 1 and tsi.get_ranking("rank") > effective_break_size:
            capped.append(tsi)

    # iv. Reinsert capped teams if there are too few breaking
    # `reinsert_correction` is how many teams "too many" we had to reinsert
    #   (if any), to be separated manually by lots
    reinsert = []
    reinsert_correction = 0
    if len(eligible) - len(capped) < break_size:
        number_to_reinsert = break_size - len(eligible) + len(capped)
        for _, group in groupby(capped, key=lambda tsi: tuple(tsi.itermetrics())):
            group = list(group)
            reinsert.extend(group)
            if len(reinsert) >= number_to_reinsert:
                reinsert_correction = len(reinsert) - number_to_reinsert
                break

    logger.info("Reinsert correction: %s", reinsert_correction)

    filtered = [tsi for tsi in eligible if tsi not in capped or tsi in reinsert]

    logger.info("Filtered list: %s", filtered)

    # v. Calculate break ranks
    break_seq = 0
    break_rank = 0
    prev_rank = None
    prev_break_rank = None
    breaking_teams = []
    breaking_teams_to_create = []
    for tsi in standings:

        team = tsi.team
        try:
            bt = BreakingTeam.objects.get(break_category=category, team=team)
            existing = True
        except BreakingTeam.DoesNotExist:
            bt = BreakingTeam(break_category=category, team=team)
            existing = False # don't want to save (so can't use get_or_create())

        bt.rank = tsi.get_ranking("rank")
        if bt.rank != prev_rank and len(breaking_teams) >= break_size:
            break # if we have enough teams, we're done
        prev_rank = bt.rank

        if tsi in filtered:
            break_seq += 1
            if len(reinsert) > 0 and tsi == reinsert[-1]:
                break_rank -= reinsert_correction
            if bt.rank != prev_break_rank:
                break_rank = break_seq
            prev_break_rank = bt.rank
            bt.break_rank = break_rank
            breaking_teams.append(team)

        elif tsi in existing_remark:
            bt.break_rank = None # scrub break rank
        elif tsi in capped:
            bt.remark = bt.REMARK_CAPPED
        elif tsi in different_break:
            bt.remark = bt.REMARK_DIFFERENT_BREAK
        elif tsi in ineligible:
            bt.remark = bt.REMARK_INELIGIBLE

        logger.info("Breaking in %s (%s) - %s", bt.break_rank, bt.get_remark_display(), bt.team.short_name)

        bt.full_clean()
        if existing:
            bt.save()
        else:
            breaking_teams_to_create.append(bt)

    BreakingTeam.objects.bulk_create(breaking_teams_to_create)
    BreakingTeam.objects.filter(break_category=category, break_rank__isnull=False).exclude(
        team_id__in=[t.id for t in breaking_teams]).delete()

    return breaking_teams


def _generate_breaking_teams_pre_2015(category, teams, teams_broken_higher_priority=set()):
    """Generates a list of breaking teams for the given category and returns
    a list of teams in the (actual) break, i.e. excluding teams that are
    ineligible, capped, broke in a different break, and so on."""

    metrics = category.tournament.pref('team_standings_precedence')
    generator = TeamStandingsGenerator(metrics, ('rank',))
    standings = generator.generate(teams)

    break_size = category.break_size
    institution_cap = category.institution_cap if category.rule == category.BREAK_QUALIFICATION_RULE_AIDA_PRE_2015 \
            else None
    assert category.rule != category.BREAK_QUALIFICATION_RULE_AIDA_2016

    prev_rank_value = tuple([None] * len(standings.metric_keys))
    prev_break_rank_value = tuple([None] * len(standings.metric_keys))
    cur_rank = 0
    breaking_teams = list()
    breaking_teams_to_create = list()

    # Variables for institutional caps and non-breaking teams
    cur_break_rank = 0 # actual break rank
    cur_break_seq = 0  # sequential count of breaking teams
    teams_from_institution = Counter()

    for i, standing in enumerate(standings, start=1):

        team = standing.team

        try:
            bt = BreakingTeam.objects.get(break_category=category, team=team)
            existing = True
        except BreakingTeam.DoesNotExist:
            bt = BreakingTeam(break_category=category, team=team)
            existing = False

        # Compute overall rank
        rank_value = tuple(standing.itermetrics())
        if rank_value != prev_rank_value:
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
        elif institution_cap is not None and teams_from_institution[team.institution] >= institution_cap:
            bt.remark = bt.REMARK_CAPPED

        # Check if already broken to a higher category
        elif team in teams_broken_higher_priority:
            bt.remark = bt.REMARK_DIFFERENT_BREAK

        # If neither, this team is in the break
        else:
            # Compute break rank
            cur_break_seq += 1
            if rank_value != prev_break_rank_value:
                cur_break_rank = cur_break_seq
                prev_break_rank_value = rank_value
            bt.break_rank = cur_break_rank

            breaking_teams.append(team)

        bt.full_clean()
        if existing:
            bt.save()
        else:
            breaking_teams_to_create.append(bt)

        # Take note of the institution
        teams_from_institution[team.institution] += 1

    BreakingTeam.objects.bulk_create(breaking_teams_to_create)
    BreakingTeam.objects.filter(break_category=category, break_rank__isnull=False).exclude(
        team_id__in=[t.id for t in breaking_teams]).delete()


    return breaking_teams