from tournaments.models import Round

from .models import Debate


def delete_round_draw(round, **options):
    Debate.objects.filter(round=round).delete()
    round.draw_status = Round.Status.NONE
    round.save()
