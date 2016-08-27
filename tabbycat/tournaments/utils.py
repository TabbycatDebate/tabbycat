import itertools

from django.db.models import Max

from .models import Round

BREAK_ROUND_NAMES = [
    ('Grand Final', 'GF'),
    ('Semifinals', 'SF'),
    ('Quarterfinals', 'QF'),
    ('Octofinals', 'OF'),
    ('Double-Octofinals', 'DOF'),
    ('Triple-Octofinals', 'TOF'),
]


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
