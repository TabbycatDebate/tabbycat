import logging

from django.utils.encoding import force_str
from django.utils.translation import gettext, gettext_lazy as _, pgettext_lazy

from .models import Round

logger = logging.getLogger(__name__)

SIDE_NAMES = {
    'aff-neg': {
        "0_full": _("affirmative"),
        "1_full": _("negative"),
        "0_team": _("affirmative team"),
        "1_team": _("negative team"),
        "0_abbr": _("Aff"),
        "1_abbr": _("Neg"),
    },
    'gov-opp': {
        "0_full": _("government"),
        "1_full": _("opposition"),
        "0_team": _("government team"),
        "1_team": _("opposition team"),
        "0_abbr": _("Gov"),
        "1_abbr": _("Opp"),
    },
    'prop-opp': {
        "0_full": _("proposition"),
        "1_full": _("opposition"),
        "0_team": _("proposition team"),
        "1_team": _("opposition team"),
        "0_abbr": _("Prop"),
        "1_abbr": _("Opp"),
    },
    'pro-con': {
        "0_full": _("pro"),
        "1_full": _("con"),
        "0_team": _("pro team"),
        "1_team": _("con team"),
        "0_abbr": _("Pro"),
        "1_abbr": _("Con"),
    },
    'appellant-respondent': {
        "0_full": _("appellant"),
        "1_full": _("respondent"),
        "0_team": _("appellant team"),
        "1_team": _("respondent team"),
        "0_abbr": _("App"),
        "1_abbr": _("Res"),
    },
    '1-2': {
        '0_full': '1',
        '1_full': '2',
        "0_team": _("1st team"),
        "1_team": _("2nd team"),
        "0_abbr": '1',
        "1_abbr": '2',
    },
}

BP_SIDE_NAMES = {  # stop-gap before this system gets refactored
    "0_full": _("opening government"),
    "1_full": _("opening opposition"),
    "2_full": _("closing government"),
    "3_full": _("closing opposition"),
    "0_team": _("opening government team"),
    "1_team": _("opening opposition team"),
    "2_team": _("closing government team"),
    "3_team": _("closing opposition team"),
    "0_abbr": pgettext_lazy("BP position", "OG"),
    "1_abbr": pgettext_lazy("BP position", "OO"),
    "2_abbr": pgettext_lazy("BP position", "CG"),
    "3_abbr": pgettext_lazy("BP position", "CO"),
}


def auto_make_rounds(tournament, num_rounds):
    """Makes the number of rounds specified. The first one is random and the
    rest are all power-paired. The last third of rounds (rounded down) are silent.
    This is intended as a convenience function. For anything more complicated,
    a more advanced import method should be used."""
    silent_threshold = num_rounds * 2 / 3

    for i in range(1, num_rounds+1):
        Round(
            tournament=tournament,
            seq=i,
            name=gettext("Round %(number)d") % {'number': i},
            # Translators: This stands for "Round %(number)d".
            abbreviation=gettext("R%(number)d") % {'number': i},
            stage=Round.Stage.PRELIMINARY,
            draw_type=Round.DrawType.RANDOM if (i == 1) else Round.DrawType.POWERPAIRED,
            feedback_weight=min((i-1)*0.1, 0.5),
            silent=(i > silent_threshold),
        ).save()


def get_side_name_choices():
    """Returns a list of choices for position names suitable for presentation in
    a form."""
    return [
        (code, force_str(names["0_full"]).capitalize() + ", " + force_str(names["1_full"]).capitalize())
        for code, names in SIDE_NAMES.items()
    ]


def get_side_name(tournament, side: int, name_type) -> str:
    """Like aff_name, neg_name, etc., but can be used when the side is not known
    at compile time. Example:
        get_side_name(tournament, "aff", "full")
    will return something like "Affirmative" or "Proposition" or "Gobierno",
    depending on the side name option and language setting.
    """
    if side == -1:
        return gettext('bye')
    elif tournament is None or tournament.pref('side_names') == '1-2':
        return gettext('Team %d') % (side + 1)
    elif tournament.pref('teams_in_debate') == 2:
        names = SIDE_NAMES.get(tournament.pref('side_names'), SIDE_NAMES['aff-neg'])
        return force_str(names["%d_%s" % (side, name_type)])
    elif tournament.pref('teams_in_debate') == 4:
        return force_str(BP_SIDE_NAMES.get("%d_%s" % (side, name_type), '%d' % (side + 1)))
    else:
        return gettext('Team %d') % (side + 1)


def _get_side_name(name_type):
    def _wrapped(tournament):
        names = SIDE_NAMES.get(tournament.pref('side_names'), SIDE_NAMES['aff-neg'])
        return force_str(names[name_type])
    return _wrapped


# These functions are used to grab the chosen and translated side names,
# appropriate for the tournament option for side names, and the language
# setting.
#
# For example:              aff-neg, en      prop-opp, en     gov-opp, es
#   aff_name(tournament) -> "Affirmative" or "Proposition" or "Gobierno"
#   neg_abbr(tournament) -> "Neg"         or "Opp"         or "Opo"
#
# They force evaluation, which should be okay, because they can only be used
# when the tournament is known, which is only ever true at runtime.
# Example usage: "The %s team faces the %s team." % (aff_name(tournament), neg_name(tournament))

aff_name = _get_side_name('0_full')
neg_name = _get_side_name('1_full')
aff_abbr = _get_side_name('0_abbr')
neg_abbr = _get_side_name('1_abbr')
aff_team = _get_side_name('0_team')
neg_team = _get_side_name('1_team')
