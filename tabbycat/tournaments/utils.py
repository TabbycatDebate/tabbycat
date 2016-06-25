from .models import Round


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
            draw_type=Round.DRAW_RANDOM if (i == 1) else Round.DRAW_POWERPAIRED,
            feedback_weight=min((i-1)*0.1, 0.5),
            silent=(i == num_rounds),
        ).save()


def auto_make_finals_rounds(tournament, num_rounds, num_finals, break_category):
    """Makes the number of final rounds specified. This is intended as a
    convenience function. For anything more complicated, a more advanced import
    method should be used."""

    finals_names = [
        ('Grand Final', 'GF'), ('Semi Finals', 'SF'), ('Quarter Finals', 'QF'),
        ('Octo Finals', 'OF'), ('Double-Octo Finals', 'DOF')]
    finals_names.extend(
        [('Unknown Finals', 'UF')] * (num_finals - len(finals_names)))

    j = 0
    for i in range(num_rounds+num_finals+1, num_rounds+1, -1):
        Round(
            tournament=tournament,
            break_category=break_category,
            seq=i,
            name=finals_names[j][0],
            abbreviation=finals_names[j][1],
            draw_type=Round.DRAW_FIRSTBREAK if (i == num_rounds+1) else Round.DRAW_BREAK,
            feedback_weight=min((i-1)*0.1, 0.5),
            silent=True,
        ).save()
        j += 1
