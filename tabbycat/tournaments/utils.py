import itertools

from django.db.models import Max
from django.utils.encoding import force_text
from django.utils.translation import pgettext_lazy, ugettext_lazy

from .models import Round

BREAK_ROUND_NAMES = [
    ('Grand Final', 'GF'),
    ('Semifinals', 'SF'),
    ('Quarterfinals', 'QF'),
    ('Octofinals', 'OF'),
    ('Double-Octofinals', 'DOF'),
    ('Triple-Octofinals', 'TOF'),
]


POSITION_NAMES = {
    'aff-neg': {
        "aff_full": ugettext_lazy("affirmative"),
        "neg_full": ugettext_lazy("negative"),
        # Translators: This is combined with other strings, e.g. in French it would be "de l'affirmatif"
        "aff_possessive": ugettext_lazy("affirmative's"),
        # Translators: This is combined with other strings, e.g. in French it would be "du négatif"
        "neg_possessive": ugettext_lazy("negative's"),
        "aff_team": ugettext_lazy("affirmative team"),
        "neg_team": ugettext_lazy("negative team"),
        "aff_abbr": ugettext_lazy("Aff"),
        "neg_abbr": ugettext_lazy("Neg"),
        # Translators: Capitalised first letter of "Affirmative", used in abbreviations
        "aff_initial": pgettext_lazy("team name", "A"),
        # Translators: Capitalised first letter of "Negative", used in abbreviations
        "neg_initial": pgettext_lazy("team name", "N"),
    },
    'gov-opp': {
        "aff_full": ugettext_lazy("government"),
        "neg_full": ugettext_lazy("opposition"),
        "aff_possessive": ugettext_lazy("government's"),
        "neg_possessive": ugettext_lazy("opposition's"),
        "aff_team": ugettext_lazy("government team"),
        "neg_team": ugettext_lazy("opposition team"),
        "aff_abbr": ugettext_lazy("Gov"),
        "neg_abbr": ugettext_lazy("Opp"),
        # Translators: Capitalised first letter of "Government", used in abbreviations
        "aff_initial": pgettext_lazy("team name", "G"),
        # Translators: Capitalised first letter of "Opposition", used in abbreviations
        "neg_initial": pgettext_lazy("team name", "O"),
    },
    'prop-opp': {
        "aff_full": ugettext_lazy("proposition"),
        "neg_full": ugettext_lazy("opposition"),
        "aff_possessive": ugettext_lazy("proposition's"),
        "neg_possessive": ugettext_lazy("opposition's"),
        "aff_team": ugettext_lazy("proposition team"),
        "neg_team": ugettext_lazy("opposition team"),
        "aff_abbr": ugettext_lazy("Prop"),
        "neg_abbr": ugettext_lazy("Opp"),
        # Translators: Capitalised first letter of "Proposition", used in abbreviations
        "aff_initial": pgettext_lazy("team name", "P"),
        # Translators: Capitalised first letter of "Opposition", used in abbreviations
        "neg_initial": pgettext_lazy("team name", "O"),
    },
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
            name='Round %d' % i,
            abbreviation='R%d' % i,
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
    break_rounds = itertools.chain(BREAK_ROUND_NAMES, itertools.repeat(('Unknown break round', 'UBR')))

    for i, (name, abbr) in zip(range(num_break), break_rounds):
        Round(
            tournament=tournament,
            break_category=break_category,
            seq=num_prelim+num_break-i,
            stage=Round.STAGE_ELIMINATION,
            name=name,
            abbreviation=abbr,
            draw_type=Round.DRAW_FIRSTBREAK if i == num_break-1 else Round.DRAW_BREAK,
            feedback_weight=0.5,
            silent=True,
        ).save()


def get_position_name_choices():
    """Returns a list of choices for position names suitable for presentation in
    a form."""
    return [
        (code, force_text(names["aff_full"]).capitalize() + ", " + force_text(names["neg_full"]).capitalize())
        for code, names in POSITION_NAMES.items()
    ]


def get_position_name(tournament, side, name_type):
    """Like aff_name, neg_name, etc., but can be used when the side is not known
    at compile time. Example:
        get_position_name(tournament, "aff", "full")
    will return something like "Affirmative" or "Proposition" or "Gobierno",
    depending on the position name option and language setting.
    """
    names = POSITION_NAMES.get(tournament.pref('position_names'), POSITION_NAMES['aff-neg'])
    if side not in ('aff', 'neg'):
        raise ValueError("get_position_name() side must be 'aff' or 'neg', not: %r" % side)
    return force_text(names["%s_%s" % (side, name_type)])


def _get_position_name(name_type):
    def _wrapped(tournament):
        names = POSITION_NAMES.get(tournament.pref('position_names'), POSITION_NAMES['aff-neg'])
        return force_text(names[name_type])
    return _wrapped


# These functions are used to grab the chosen and translated position names,
# appropriate for the tournament option for position names, and the language
# setting.
#
# For example:              aff-neg, en      prop-opp, en     gov-opp, es
#   aff_name(tournament) -> "Affirmative" or "Proposition" or "Gobierno"
#   neg_abbr(tournament) -> "Neg"         or "Opp"         or "Opo"
#
# They force evaluation, which should be okay, because they can only be used
# when the tournament is known, which is only ever true at runtime.
# Example usage: "The %s team faces the %s team." % (aff_name(tournament), neg_name(tournament))

aff_name = _get_position_name('aff_full')
neg_name = _get_position_name('neg_full')
aff_abbr = _get_position_name('aff_abbr')
neg_abbr = _get_position_name('neg_abbr')
aff_team = _get_position_name('aff_team')
neg_team = _get_position_name('neg_team')
aff_possessive = _get_position_name('aff_possessive')
neg_possessive = _get_position_name('neg_possessive')
aff_initial = _get_position_name('aff_initial')
neg_initial = _get_position_name('neg_initial')
