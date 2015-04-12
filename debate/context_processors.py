from debate.models import Tournament, Round
from debate.models import Config

def debate_context(request):

    if hasattr(request, 'tournament'):
        d = {
            'tournament'              : request.tournament,
            'current_round'           : request.tournament.get_current_round_cached,
            'reply_scores_enabled'    : request.tournament.config.get('reply_scores_enabled'),
            'show_emoji'              : request.tournament.config.get('show_emoji'),
            'show_institutions'       : request.tournament.config.get('show_institutions'),
            'show_novices'            : request.tournament.config.get('show_novices'),
            'show_unaccredited'       : request.tournament.config.get('show_unaccredited'),
            'motion_vetoes_enabled'   : request.tournament.config.get('motion_vetoes_enabled'),
            'public_team_standings'   : request.tournament.config.get('public_team_standings') \
                                           and request.tournament.get_current_round_cached.prev is not None,
            'public_breaking_teams'   : request.tournament.config.get('public_breaking_teams'),
            'public_breaking_adjs'    : request.tournament.config.get('public_breaking_adjs'),
            'esl_break'               : request.tournament.config.get('esl_break_size') > 0,
            'public_participants'     : request.tournament.config.get('public_participants'),
            'public_side_allocations' : request.tournament.config.get('public_side_allocations') \
                                            and request.tournament.config.get('draw_side_allocations') == "preallocated",
            'public_divisions'        : request.tournament.config.get('public_divisions'),
            'public_draw'             : request.tournament.config.get('public_draw'),
            'show_all_draws'          : request.tournament.config.get('show_all_draws'),
            'show_speakers_in_draw'   : request.tournament.config.get('show_speakers_in_draw'),
            'public_motions'          : request.tournament.config.get('public_motions'),
            'public_results'          : request.tournament.config.get('public_results'),
            'public_ballots'          : request.tournament.config.get('public_ballots'),
            'public_feedback'         : request.tournament.config.get('public_feedback'),
            'feedback_progress'       : request.tournament.config.get('feedback_progress'),
            'tab_released'            : request.tournament.config.get('tab_released'),
            'motion_tab_released'     : request.tournament.config.get('motion_tab_released'),
            'side_allocations_enabled': request.tournament.config.get('draw_side_allocations') == "preallocated",
            'side_allocations_unknown': request.tournament.config.get('draw_side_allocations') == "manual-ballot",
            'enable_flagged_motions'  : request.tournament.config.get('enable_flagged_motions'),
            'enable_adj_notes'        : request.tournament.config.get('enable_adj_notes'),
            'enable_venue_times'      : request.tournament.config.get('enable_venue_times'),
            'enable_venue_groups'     : request.tournament.config.get('enable_venue_groups'),
            'show_avg_margin'         : request.tournament.config.get('show_avg_margin'),
            'show_team_points'        : request.tournament.config.get('team_points_rule') == 'wadl',
            'enable_divisions'        : request.tournament.config.get('enable_divisions'),
            'enable_division_motions' : request.tournament.config.get('enable_division_motions'),
            'enable_forfeits'         : request.tournament.config.get('enable_forfeits'),
            'enable_postponements'    : request.tournament.config.get('enable_postponements'),
        }
        if hasattr(request, 'round'):
            d['round'] = request.round
        d['all_tournaments'] = Tournament.objects.filter(active=True)
        return d

    return {}
