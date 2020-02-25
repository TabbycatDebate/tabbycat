import logging
from itertools import combinations

from django.db.models import Count
from django.contrib.humanize.templatetags.humanize import ordinal
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from draw.models import Debate
from options.utils import use_team_code_names
from tournaments.utils import get_side_name

logger = logging.getLogger(__name__)


def get_status_meta(debate):
    if debate.result_status == Debate.STATUS_NONE:
        return "x", "text-danger", 0, _("No Ballot")
    elif debate.result_status == Debate.STATUS_DRAFT:
        return "circle", "text-info", 2, _("Ballot is Unconfirmed")
    elif debate.result_status == Debate.STATUS_CONFIRMED:
        return "check", "text-success", 3, _("Ballot is Confirmed")
    else:
        raise ValueError('Debate has no discernable status')


def readable_ballotsub_result(ballotsub):
    """ Make a human-readable representation of a debate result """

    def format_dt(dt, t, use_codes):
        # Translators: e.g. "{Melbourne 1} as {OG}", "{Cape Town 1} as {CO}"
        return _("%(team_name)s as %(side_abbr)s") % {
            'team_name': dt.team.code_name if use_codes else dt.team.short_name,
            'side_abbr': dt.get_side_abbr(t),
        }

    t = ballotsub.debate.round.tournament
    team_scores = ballotsub.teamscore_set.all()
    use_codes = use_team_code_names(t, True)

    try:
        if t.pref('teams_in_debate') == 'two':
            winner = None
            loser = None
            for teamscore in team_scores:
                if teamscore.win:
                    winner = teamscore.debate_team
                else:
                    loser = teamscore.debate_team

            result_winner = _("%(winner)s (%(winner_side)s) won")
            result_winner = result_winner % {
                'winner': winner.team.code_name if use_codes else winner.team.short_name,
                'winner_side': winner.get_side_abbr(t),
            }
            result = _("vs %(loser)s (%(loser_side)s)")
            result = result % {
                'loser': loser.team.code_name if use_codes else loser.team.short_name,
                'loser_side': loser.get_side_abbr(t),
            }

        elif ballotsub.debate.round.is_break_round:
            advancing = []
            eliminated = []
            for teamscore in team_scores:
                if teamscore.win:
                    advancing.append(teamscore.debate_team)
                else:
                    eliminated.append(teamscore.debate_team)

            result_winner = _("Advancing: %(advancing_list)s<br>\n")
            result_winner = result_winner % {
                'advancing_list': ", ".join(format_dt(dt, t, use_codes) for dt in advancing),
            }
            result = _("Eliminated: %(eliminated_list)s")
            result = result % {
                'eliminated_list': ", ".join(format_dt(dt, t, use_codes) for dt in eliminated),
            }

        else:  # BP preliminary round
            ordered = [None] * 4
            for teamscore in team_scores:
                ordered[teamscore.points] = teamscore.debate_team

            result_winner = _("1st: %(first_team)s<br>\n")
            result_winner = result_winner % {'first_team':  format_dt(ordered[3], t, use_codes)}
            result = _("2nd: %(second_team)s<br>\n"
                       "3rd: %(third_team)s<br>\n"
                       "4th: %(fourth_team)s")
            result = result % {
                'second_team': format_dt(ordered[2], t, use_codes),
                'third_team':  format_dt(ordered[1], t, use_codes),
                'fourth_team': format_dt(ordered[0], t, use_codes),
            }

    except (IndexError, AttributeError):
        logger.warning("Error constructing latest result string", exc_info=True)
        if use_codes:
            matchup = ballotsub.debate.matchup_codes
        else:
            matchup = ballotsub.debate.matchup
        result_winner = _("Error with result for %(debate)s") % {'debate': matchup}
        result = ""

    return result_winner, result


def set_float_or_int(number, step_value):
    """Used to ensure the values sent through to the frontend <input> are
    either Ints or Floats such that the validation can handle them properly"""
    if step_value.is_integer():
        return int(number)
    else:
        return number


def get_result_status_stats(round):
    """Returns a dict where keys are result statuses of debates; values are the
    number of debates in the round with that status.

    There is also an additional key 'B' that denotes those with ballots checked
    in, but whose results are not entered."""

    # query looks like: [{'result_status': 'C', 'result_status__count': 8}, ...]
    query = round.debate_set.values('result_status').annotate(Count('result_status')).order_by()

    # The query doesn't return zeroes where appropriate - for statuses with no
    # debates, it just omits the item altogether. So initialize a dict:
    choices = [code for code, name in Debate.STATUS_CHOICES]
    stats = dict.fromkeys(choices, 0)
    for item in query:
        stats[item['result_status']] = item['result_status__count']

    return stats


def populate_identical_ballotsub_lists(ballotsubs):
    """Sets an attribute `identical_ballotsub_versions` on each BallotSubmission
    in `ballotsubs` to a list of version numbers of the other BallotSubmissions
    that are identical to it.

    Two ballot submissions are identical if they share the same debate, motion,
    speakers and all speaker scores."""

    from .prefetch import populate_results
    populate_results(ballotsubs)

    for ballotsub in ballotsubs:
        ballotsub.identical_ballotsub_versions = []

    for ballotsub1, ballotsub2 in combinations(ballotsubs, 2):
        if ballotsub1.result.identical(ballotsub2.result):
            ballotsub1.identical_ballotsub_versions.append(ballotsub2.version)
            ballotsub2.identical_ballotsub_versions.append(ballotsub1.version)

    for ballotsub in ballotsubs:
        ballotsub.identical_ballotsub_versions.sort()


_BP_POSITION_NAMES = [
    # Translators: Abbreviation for Prime Minister
    [gettext_lazy("PM"),
    # Translators: Abbreviation for Deputy Prime Minister
     gettext_lazy("DPM")],
    # Translators: Abbreviation for Leader of the Opposition
    [gettext_lazy("LO"),
    # Translators: Abbreviation for Deputy Leader of the Opposition
     gettext_lazy("DLO")],
    # Translators: Abbreviation for Member for the Government
    [gettext_lazy("MG"),
    # Translators: Abbreviation for Government Whip
     gettext_lazy("GW")],
    # Translators: Abbreviation for Member for the Opposition
    [gettext_lazy("MO"),
    # Translators: Abbreviation for Opposition Whip
     gettext_lazy("OW")],
]


def side_and_position_names(tournament):
    """Yields 2-tuples (side, positions), where position is a list of position
    names, all being translated human-readable names. This should eventually
    be extended to return an appropriate list for the tournament configuration.
    """
    sides = [get_side_name(tournament, side, 'full').title() for side in tournament.sides]

    if tournament.pref('teams_in_debate') == 'bp' \
            and tournament.last_substantive_position == 2 \
            and tournament.reply_position is None:

        for side, positions in zip(sides, _BP_POSITION_NAMES):
            yield side, positions

    else:
        for side in sides:
            positions = [_("Reply") if pos == tournament.reply_position
                else ordinal(pos)
                for pos in tournament.positions]
            yield side, positions
