from .models import Debate
from tournaments.models import Round


def delete_round_draw(round, **options):
    Debate.objects.filter(round=round).delete()
    round.draw_status = Round.STATUS_NONE
    round.save()
