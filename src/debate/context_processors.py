from debate.models import Tournament 

def debate_context(request):
    return {
        'current_round': Tournament().current_round, 
    }

