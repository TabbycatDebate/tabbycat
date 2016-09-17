import itertools

from django.db.models import Max
from django.utils.encoding import force_text
from django.utils.translation import pgettext_lazy, string_concat, ugettext_lazy

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
        "aff_full": ugettext_lazy("Affirmative"),
        "neg_full": ugettext_lazy("Negative"),
        "aff_abbr": ugettext_lazy("Aff"),
        "neg_abbr": ugettext_lazy("Neg"),
        # Translators: This should be the first letter of "Affirmative", or something that can be used in abbreviations
        "aff_init": pgettext_lazy("team name", "A"),
        # Translators: This should be the first letter of "Negative", or something that can be used in abbreviations
        "neg_init": pgettext_lazy("team name", "N"),
    },
    'gov-opp': {
        "aff_full": ugettext_lazy("Government"),
        "neg_full": ugettext_lazy("Opposition"),
        "aff_abbr": ugettext_lazy("Gov"),
        "neg_abbr": ugettext_lazy("Opp"),
        # Translators: This should be the first letter of "Government", or something that can be used in abbreviations
        "aff_init": pgettext_lazy("team name", "G"),
        # Translators: This should be the first letter of "Opposition", or something that can be used in abbreviations
        "neg_init": pgettext_lazy("team name", "O"),
    },
    'prop-opp': {
        "aff_full": ugettext_lazy("Proposition"),
        "neg_full": ugettext_lazy("Opposition"),
        "aff_abbr": ugettext_lazy("Prop"),
        "neg_abbr": ugettext_lazy("Opp"),
        # Translators: This should be the first letter of "Proposition", or something that can be used in abbreviations
        "aff_init": pgettext_lazy("team name", "P"),
        # Translators: This should be the first letter of "Opposition", or something that can be used in abbreviations
        "neg_init": pgettext_lazy("team name", "O"),
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
        (code, string_concat(names["aff_full"], ", ", names["neg_full"]))
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
aff_initial = _get_position_name('aff_init')
neg_initial = _get_position_name('neg_init')
