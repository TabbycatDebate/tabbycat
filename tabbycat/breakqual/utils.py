import itertools
import logging

from django.db.models import Count, Max, Q, Sum
from django.utils.translation import gettext_lazy as _

from standings.teams import TeamStandingsGenerator
from tournaments.models import Round

from .liveness import liveness_bp, liveness_twoteam

logger = logging.getLogger(__name__)


def get_breaking_teams(category, prefetch=(), rankings=('rank',)):
    """Returns a list of StandingInfo objects, one for each team, with one
    additional attribute populated: for each StandingInfo `tsi`,
    `tsi.break_rank` is the rank of the team out of those that are in the break.

    `prefetch` is passed to `prefetch_related()` in the Team query.
    `rankings` is passed to `rankings` in the TeamStandingsGenerator.
    """
    teams = category.breaking_teams.all().prefetch_related(*prefetch)
    metrics = category.tournament.pref('team_standings_precedence')
    generator = TeamStandingsGenerator(metrics, rankings)
    standings = generator.generate(teams)

    breakingteams_by_team_id = {bt.team_id: bt for bt in category.breakingteam_set.all()}

    for tsi in standings:

        bt = breakingteams_by_team_id[tsi.team.id]
        if bt.break_rank is None:
            if bt.remark:
                tsi.break_rank = "(" + bt.get_remark_display().lower() + ")"
            else:
                tsi.break_rank = "<no rank, no remark>"
        else:
            tsi.break_rank = bt.break_rank

    return standings


def breakcategories_with_counts(tournament):
    categories = tournament.breakcategory_set.annotate(
        eligible=Count('team', distinct=True),
        breaking=Count('breakingteam', filter=Q(breakingteam__break_rank__isnull=False), distinct=True),
        excluded=Count('breakingteam', filter=Q(breakingteam__break_rank__isnull=True), distinct=True),
    )
    for category in categories:
        category.nonbreaking = category.eligible - category.breaking
    return categories


def liveness(self, team, teams_count, prelims, current_round):
    live_info = {'text': team.wins_count, 'tooltip': ''}

    # The actual calculation should be shifed to be a cached method on
    # the relevant break category
    highest_liveness = 3
    for bc in team.break_categories.all():
        import random
        status = random.choice([1, 2, 3])
        highest_liveness = 3
        if status == 1:
            live_info['tooltip'] += 'Definitely in for the %s break<br>test' % bc.name
            if highest_liveness != 2:
                highest_liveness = 1  # Live not ins are the most important highlight
        elif status == 2:
            live_info['tooltip'] += 'Still live for the %s break<br>test' % bc.name
            highest_liveness = 2
        elif status == 3:
            live_info['tooltip'] += 'Cannot break in %s break<br>test' % bc.name

    if highest_liveness == 1:
        live_info['class'] = 'bg-success'
    elif highest_liveness == 2:
        live_info['class'] = 'bg-warning'

    return live_info


def determine_liveness(thresholds, points):
    """ Thresholds should be calculated using calculate_live_thresholds."""
    safe, dead = thresholds
    if points is None:
        points = 0 # For when a results-less team (i.e. swings) is subbing in

    if safe is None and dead is None:
        return '?'
    elif points >= safe:
        return 'safe'
    elif points <= dead:
        return 'dead'
    else:
        return 'live'


def calculate_live_thresholds(bc, tournament, round):
    total_teams = tournament.team_set.count()
    total_rounds = tournament.prelim_rounds().count()

    if not bc.is_general:
        team_scores = bc.team_set.filter(
            debateteam__debate__round__seq__lt=round.seq,
            debateteam__teamscore__ballot_submission__confirmed=True,
        ).annotate(score=Sum('debateteam__teamscore__points')).values_list('score', flat=True)
        team_scores = list(team_scores)
        team_scores += [0] * (bc.team_set.count() - len(team_scores))
    else:
        team_scores = None

    if bc.break_size <= 1 or total_teams == 0:
        return None, None # Bad input
    elif tournament.pref('teams_in_debate') == 'bp':
        safe, dead = liveness_bp(bc.is_general, round.seq, bc.break_size,
                            total_teams, total_rounds, team_scores)
    else:
        safe, dead = liveness_twoteam(bc.is_general, round.seq, bc.break_size,
                              total_teams, total_rounds, team_scores)

    logger.info("Liveness in %s R%d/%d with break size %d, %d teams: safe at %d, dead at %d",
        tournament.short_name, round.seq, total_rounds, bc.break_size, total_teams, safe, dead)
    return safe, dead


BREAK_ROUND_NAMES = [
    # Translators: abbreviation for "grand final"
    (_("Grand Final"), _("GF")),
    # Translators: abbreviation for "semifinals"
    (_("Semifinals"), _("SF")),
    # Translators: abbreviation for "quarterfinals"
    (_("Quarterfinals"), _("QF")),
    # Translators: abbreviation for "octofinals"
    (_("Octofinals"), _("OF")),
    # Translators: abbreviation for "double-octofinals"
    (_("Double-Octofinals"), _("DOF")),
    # Translators: abbreviation for "triple-octofinals"
    (_("Triple-Octofinals"), _("TOF")),
]


def get_break_category_round_names(bc):
    return [
        # Translators: abbreviation for "finals" - first character of category name
        (_("%s Finals") % (bc.name), _("%sF") % (bc.name[:1])),
        # Translators: abbreviation for "semifinals" - first character of category name
        (_("%s Semifinals") % (bc.name), _("%sSF") % (bc.name[:1])),
        # Translators: abbreviation for "quarterfinals" - first character of category name
        (_("%s Quarterfinals") % (bc.name), _("%sQF") % (bc.name[:1])),
        # Translators: abbreviation for "octofinals" - first character of category name
        (_("%s Octofinals") % (bc.name), _("%sOF") % (bc.name[:1])),
        # Translators: abbreviation for "double-octofinals" - first character of category name
        (_("%s Double-Octofinals") % (bc.name), _("%sDOF") % (bc.name[:1])),
        # Translators: abbreviation for "triple-octofinals" - first character of category name
        (_("%s Triple-Octofinals") % (bc.name), _("%sTOF") % (bc.name[:1])),
    ]


def auto_make_break_rounds(bc, tournament=None, prefix=False):
    if tournament is None:
        tournament = bc.tournament

    num_rounds = tournament.round_set.all().aggregate(Max('seq'))['seq__max']
    round_names = get_break_category_round_names(bc) if prefix else BREAK_ROUND_NAMES

    # Translators: "UBR" stands for "unknown break round" (used as a fallback when we don't know what it's called)
    unknown_round = (_("Unknown %s break round") % (bc.name), _("U%sBR") % (bc.name[:1])) if prefix \
        else (_("Unknown break round"), _("UBR"))

    break_rounds = itertools.chain(round_names, itertools.repeat(unknown_round))

    for i, (name, abbr) in zip(range(bc.num_break_rounds), break_rounds):
        Round(
            tournament=tournament,
            break_category=bc,
            seq=num_rounds+bc.num_break_rounds-i,
            stage=Round.STAGE_ELIMINATION,
            name=name,
            abbreviation=abbr,
            draw_type=Round.DRAW_ELIMINATION,
            feedback_weight=0.5,
            silent=True,
        ).save()
