from debate.models import Tournament, Round 

def debate_context(request):
    return {
        'current_round': Tournament().current_round, 
        'rounds': Round.objects.all(),
    }

