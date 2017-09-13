import itertools

from django.db.models import Max
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy, ugettext

from .models import Round


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

SIDE_NAMES = {
    'aff-neg': {
        "aff_full": _("affirmative"),
        "neg_full": _("negative"),
        # Translators: This is combined with other strings, e.g. in French it would be "de l'affirmatif"
        "aff_possessive": _("affirmative's"),
        # Translators: This is combined with other strings, e.g. in French it would be "du négatif"
        "neg_possessive": _("negative's"),
        "aff_team": _("affirmative team"),
        "neg_team": _("negative team"),
        "aff_abbr": _("Aff"),
        "neg_abbr": _("Neg"),
        # Translators: Capitalised first letter of "Affirmative", used in abbreviations
        "aff_initial": pgettext_lazy("team name", "A"),
        # Translators: Capitalised first letter of "Negative", used in abbreviations
        "neg_initial": pgettext_lazy("team name", "N"),
    },
    'gov-opp': {
        "aff_full": _("government"),
        "neg_full": _("opposition"),
        "aff_possessive": _("government's"),
        "neg_possessive": _("opposition's"),
        "aff_team": _("government team"),
        "neg_team": _("opposition team"),
        "aff_abbr": _("Gov"),
        "neg_abbr": _("Opp"),
        # Translators: Capitalised first letter of "Government", used in abbreviations
        "aff_initial": pgettext_lazy("team name", "G"),
        # Translators: Capitalised first letter of "Opposition", used in abbreviations
        "neg_initial": pgettext_lazy("team name", "O"),
    },
    'prop-opp': {
        "aff_full": _("proposition"),
        "neg_full": _("opposition"),
        "aff_possessive": _("proposition's"),
        "neg_possessive": _("opposition's"),
        "aff_team": _("proposition team"),
        "neg_team": _("opposition team"),
        "aff_abbr": _("Prop"),
        "neg_abbr": _("Opp"),
        # Translators: Capitalised first letter of "Proposition", used in abbreviations
        "aff_initial": pgettext_lazy("team name", "P"),
        # Translators: Capitalised first letter of "Opposition", used in abbreviations
        "neg_initial": pgettext_lazy("team name", "O"),
    },
    'pro-con': {
        "aff_full": _("pro"),
        "neg_full": _("con"),
        "aff_possessive": _("pro's"),
        "neg_possessive": _("con's"),
        "aff_team": _("pro team"),
        "neg_team": _("con team"),
        "aff_abbr": _("Pro"),
        "neg_abbr": _("Con"),
        # Translators: Capitalised first letter of "Pro", used in abbreviations
        "aff_initial": pgettext_lazy("team name", "P"),
        # Translators: Capitalised first letter of "Con", used in abbreviations
        "neg_initial": pgettext_lazy("team name", "C"),
    },
}

BP_SIDE_NAMES = {  # stop-gap before this system gets refactored
    "og_full": _("opening government"),
    "oo_full": _("opening opposition"),
    "cg_full": _("closing government"),
    "co_full": _("closing opposition"),
    "og_possessive": _("opening government's"),
    "oo_possessive": _("opening opposition's"),
    "cg_possessive": _("closing government's"),
    "co_possessive": _("closing opposition's"),
    "og_team": _("opening government team"),
    "oo_team": _("opening opposition team"),
    "cg_team": _("closing government team"),
    "co_team": _("closing opposition team"),
    "og_abbr": pgettext_lazy("team name", "OG"),
    "oo_abbr": pgettext_lazy("team name", "OO"),
    "cg_abbr": pgettext_lazy("team name", "CG"),
    "co_abbr": pgettext_lazy("team name", "CO"),
    "og_initial": pgettext_lazy("team name", "OG"),
    "oo_initial": pgettext_lazy("team name", "OO"),
    "cg_initial": pgettext_lazy("team name", "CG"),
    "co_initial": pgettext_lazy("team name", "CO"),
}


def auto_make_rounds(tournament, num_rounds):
    """Makes the number of rounds specified. The first one is random and the
    rest are all power-paired. The last one is silent. This is intended as a
    convenience function. For anything more complicated, a more advanced import
    method should be used."""
    for i in range(1, num_rounds+1):
        Round(
            tournament=tournament,
            seq=i,
            name=ugettext("Round %(number)d") % {'number': i},
            # Translators: This stands for "Round %(number)d".
            abbreviation=ugettext("R%(number)d") % {'number': i},
            stage=Round.STAGE_PRELIMINARY,
            draw_type=Round.DRAW_RANDOM if (i == 1) else Round.DRAW_POWERPAIRED,
            feedback_weight=min((i-1)*0.1, 0.5),
            silent=(i == num_rounds),
        ).save()


def auto_make_break_rounds(tournament, num_break, break_category):
    """Makes the number of break rounds specified. This is intended as a
    convenience function. For anything more complicated, a more advanced import
    method should be used."""

    num_prelim = tournament.prelim_rounds().aggregate(Max('seq'))['seq__max']
    # Translators: "UBR" stands for "unknown break round" (used as a fallback when we don't know what it's called)
    break_rounds = itertools.chain(BREAK_ROUND_NAMES, itertools.repeat((_("Unknown break round"), _("UBR"))))

    for i, (name, abbr) in zip(range(num_break), break_rounds):
        Round(
            tournament=tournament,
            break_category=break_category,
            seq=num_prelim+num_break-i,
            stage=Round.STAGE_ELIMINATION,
            name=name,
            abbreviation=abbr,
            draw_type=Round.DRAW_ELIMINATION,
            feedback_weight=0.5,
            silent=True,
        ).save()


def get_side_name_choices():
    """Returns a list of choices for position names suitable for presentation in
    a form."""
    return [
        (code, force_text(names["aff_full"]).capitalize() + ", " + force_text(names["neg_full"]).capitalize())
        for code, names in SIDE_NAMES.items()
    ]


def get_side_name(tournament, side, name_type):
    """Like aff_name, neg_name, etc., but can be used when the side is not known
    at compile time. Example:
        get_side_name(tournament, "aff", "full")
    will return something like "Affirmative" or "Proposition" or "Gobierno",
    depending on the side name option and language setting.
    """
    if side in ('aff', 'neg'):
        names = SIDE_NAMES.get(tournament.pref('side_names'), SIDE_NAMES['aff-neg'])
        return force_text(names["%s_%s" % (side, name_type)])
    elif side in ('og', 'oo', 'cg', 'co'):
        return force_text(BP_SIDE_NAMES["%s_%s" % (side, name_type)])
    else:
        raise ValueError("get_side_name() side must be one of: 'aff', 'neg', 'og', 'oo', 'cg', 'co', not: %r" % side)


def _get_side_name(name_type):
    def _wrapped(tournament):
        names = SIDE_NAMES.get(tournament.pref('side_names'), SIDE_NAMES['aff-neg'])
        return force_text(names[name_type])
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

aff_name = _get_side_name('aff_full')
neg_name = _get_side_name('neg_full')
aff_abbr = _get_side_name('aff_abbr')
neg_abbr = _get_side_name('neg_abbr')
aff_team = _get_side_name('aff_team')
neg_team = _get_side_name('neg_team')
aff_possessive = _get_side_name('aff_possessive')
neg_possessive = _get_side_name('neg_possessive')
aff_initial = _get_side_name('aff_initial')
neg_initial = _get_side_name('neg_initial')
