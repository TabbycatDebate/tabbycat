from django.shortcuts import get_object_or_404

from debate.models import Tournament, Round

class DebateMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'tournament_slug' in view_kwargs:
            request.tournament = get_object_or_404(Tournament,
                                                   slug=view_kwargs['tournament_slug'])
            if 'round_seq' in view_kwargs:
                request.round = get_object_or_404(Round,
                                                  tournament=request.tournament,
                                                  seq=view_kwargs['round_seq'])

        return None

