from django.conf.urls import *

from django.core.urlresolvers import reverse

from debate import models as m

urlpatterns = patterns('debate.views',
    url(r'^admin/$', 'tournament_home', name='tournament_home'),
    url(r'^admin/results_status_update/$', 'results_status_update', name='results_status_update'),
    url(r'^admin/action_log_update/$', 'action_log_update', name='action_log_update'),
    url(r'^admin/config/$', 'tournament_config', name='tournament_config'),
    url(r'^admin/draw/$', 'draw_index', name='draw_index'),
    url(r'^admin/round/(?P<round_seq>\d+)/$', 'round_index', name='round_index'),

    url(r'^$', 'public_index', name='public_index'),
    url(r'^draw/$', 'public_draw', name='public_draw'),
    url(r'^draw/round/(?P<round_seq>\d+)/$', 'public_draw_by_round', name='public_draw_by_round'),
    url(r'^draw/all/$', 'public_all_draws', name='public_all_draws'),
    url(r'^results/$', 'public_results_index', name='public_results_index'),
    url(r'^results/round/(?P<round_seq>\d+)/$', 'public_results', name='public_results'),

    url(r'^team_speakers/(?P<team_id>\d+)/$', 'team_speakers', name='team_speakers'),

    url(r'^break/$', 'public_break_index', name='public_break_index'),
    url(r'^break/teams/(?P<category>\w+)/$', 'public_breaking_teams', name='public_breaking_teams'),
    url(r'^break/adjudicators/$',  'public_breaking_adjs', name='public_breaking_adjs'),

    url(r'^add_ballot/$', 'public_ballot_submit', name='public_ballot_submit'),
    url(r'^add_ballot/adjudicator/(?P<adj_id>\d+)/$', 'public_new_ballotset_id', name='public_new_ballotset'),
    url(r'^add_ballot/adjudicator/h/(?P<url_key>\w+)/$', 'public_new_ballotset_key', name='public_new_ballotset_key'),
    url(r'^add_feedback/$', 'public_feedback_submit', name='public_feedback_submit'),
    url(r'^add_feedback/team/(?P<source_id>\d+)/$', 'public_enter_feedback_id', {'source_type': m.Team}, name='public_enter_feedback_team'),
    url(r'^add_feedback/team/h/(?P<url_key>\w+)/$', 'public_enter_feedback_key', {'source_type': m.Team}, name='public_enter_feedback_team_key'),
    url(r'^add_feedback/adjudicator/(?P<source_id>\d+)/$', 'public_enter_feedback_id', {'source_type': m.Adjudicator}, name='public_enter_feedback_adjudicator'),
    url(r'^add_feedback/adjudicator/h/(?P<url_key>\w+)/$', 'public_enter_feedback_key', {'source_type': m.Adjudicator}, name='public_enter_feedback_adjudicator_key'),
    url(r'^toggle_postponed/$', 'toggle_postponed', name='toggle_postponed'),

    url(r'^feedback_progress/$', 'public_feedback_progress', name='public_feedback_progress'),
    url(r'^participants/$', 'public_participants', name='public_participants'),
    url(r'^motions/$', 'public_motions', name='public_motions'),
    url(r'^divisions/$', 'public_divisions', name='public_divisions'),
    url(r'^side_allocations/$', 'public_side_allocations', name='public_side_allocations'),
    url(r'^standings/$', 'public_team_standings', name='public_team_standings'),

    url(r'^tab/team/$', 'public_team_tab', name='public_team_tab'),
    url(r'^tab/speaker/$', 'public_speaker_tab', name='public_speaker_tab'),
    url(r'^tab/novices/$', 'public_novices_tab', name='public_novices_tab'),
    url(r'^tab/replies/$', 'public_replies_tab', name='public_replies_tab'),
    url(r'^tab/motions/$', 'public_motions_tab', name='public_motions_tab'),
    url(r'^ballots/debate/(?P<debate_id>\d+)/$', 'public_ballots_view', name='public_ballots_view'),

    #url(r'^admin/actions/$', 'action_log', name='action_log'),

    url(r'^admin/round/(?P<round_seq>\d+)/venues/$', 'availability', { 'model': 'venue', 'context_name': 'venues' }, 'venue_availability'),
    url(r'^admin/round/(?P<round_seq>\d+)/venues/update/$',
        'update_availability', { 'active_attr': 'venue', 'active_model': m.ActiveVenue, 'update_method': 'set_available_venues' }, 'update_venue_availability'),

    url(r'^admin/round/(?P<round_seq>\d+)/adjudicators/$', 'availability', { 'model': 'adjudicator', 'context_name': 'adjudicators' }, 'adjudicator_availability'),
    url(r'^admin/round/(?P<round_seq>\d+)/adjudicators/update/$',
        'update_availability', { 'active_attr': 'adjudicator', 'active_model': m.ActiveAdjudicator, 'update_method': 'set_available_adjudicators' }, 'update_adjudicator_availability'),

    url(r'^admin/round/(?P<round_seq>\d+)/people/$', 'checkin_results', { 'model': 'person', 'context_name': 'people' }, 'people_availability'),
    url(r'^admin/round/(?P<round_seq>\d+)/people/update/$',
        'checkin_update', { 'active_attr': None, 'active_model': None, 'update_method': 'set_available_people' }, 'update_people_availability'),

    url(r'^admin/round/(?P<round_seq>\d+)/teams/$', 'availability', { 'model': 'team', 'context_name': 'teams' }, 'team_availability'),
    url(r'^admin/round/(?P<round_seq>\d+)/teams/update/$',
        'update_availability', { 'active_attr': 'team', 'active_model': m.ActiveTeam, 'update_method': 'set_available_teams' }, 'update_team_availability'),

    url(r'^admin/round/(?P<round_seq>\d+)/checkin/$', 'checkin', name='checkin'),
    url(r'^admin/round/(?P<round_seq>\d+)/checkin/post/$', 'post_checkin', name='post_checkin'),

    url(r'^admin/round/(?P<round_seq>\d+)/draw/$', 'draw', name='draw'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/details/$', 'draw_with_standings', name='draw_with_standings'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw_display_by_venue/$', 'draw_display_by_venue', name='draw_display_by_venue'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw_display_by_team/$', 'draw_display_by_team', name='draw_display_by_team'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/create/$', 'create_draw', name='create_draw'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/create_draw_with_all_teams/$', 'create_draw_with_all_teams', name='create_draw_with_all_teams'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/confirm/$', 'confirm_draw', name='confirm_draw'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/release/$', 'release_draw', name='release_draw'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/unrelease/$', 'unrelease_draw', name='unrelease_draw'),

    url(r'^admin/round/(?P<round_seq>\d+)/draw/matchups/edit/$', 'draw_matchups_edit', name='draw_matchups_edit'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/matchups/save/$', 'save_matchups', name='save_matchups'),

    url(r'^admin/round/(?P<round_seq>\d+)/draw/venues/$', 'draw_venues_edit', name='draw_venues_edit'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/venues/save/$', 'save_venues', name='save_venues'),

    url(r'^admin/round/(?P<round_seq>\d+)/draw/print/scoresheets/$', 'draw_print_scoresheets', name='draw_print_scoresheets'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/print/feedback/$', 'draw_print_feedback', name='draw_print_feedback'),

    url(r'^admin/round/(?P<round_seq>\d+)/draw/adjudicators/$', 'draw_adjudicators_edit', name='draw_adjudicators_edit'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/adjudicators/_get/$', 'draw_adjudicators_get', name='draw_adjudicators_get'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/adjudicators/save/$', 'save_adjudicators', name='save_adjudicators'),
    url(r'^admin/round/(?P<round_seq>\d+)/_update_importance/$', 'update_debate_importance', name='update_debate_importance'),


    url(r'^admin/round/(?P<round_seq>\d+)/round_increment_check/$', 'round_increment_check', name='round_increment_check'),
    url(r'^admin/round/(?P<round_seq>\d+)/round_increment/$', 'round_increment', name='round_increment'),

    url(r'^admin/round/(?P<round_seq>\d+)/adj_allocation/create/$', 'create_adj_allocation', name='create_adj_allocation'),
    url(r'^admin/round/(?P<round_seq>\d+)/motions/$', 'motions', name='motions'),
    url(r'^admin/round/(?P<round_seq>\d+)/motions/edit/$', 'motions_edit', name='motions_edit'),
    url(r'^admin/round/(?P<round_seq>\d+)/motions/assign/$', 'motions_assign', name='motions_assign'),
    url(r'^admin/round/(?P<round_seq>\d+)/motions/release/$', 'release_motions', name='release_motions'),
    url(r'^admin/round/(?P<round_seq>\d+)/motions/unrelease/$', 'unrelease_motions', name='unrelease_motions'),
    url(r'^admin/round/(?P<round_seq>\d+)/start_time/set/$', 'set_round_start_time', name='set_round_start_time'),

    url(r'^admin/round/(?P<round_seq>\d+)/results/$', 'results', name='results'),
    url(r'^admin/round/(?P<round_seq>\d+)/standings/team/$', 'team_standings', name='team_standings'),
    url(r'^admin/round/(?P<round_seq>\d+)/standings/division/$', 'division_standings', name='division_standings'),
    url(r'^admin/round/(?P<round_seq>\d+)/standings/speaker/$', 'speaker_standings', name='speaker_standings'),
    url(r'^admin/round/(?P<round_seq>\d+)/standings/novices/$', 'novice_standings', name='novice_standings'),
    url(r'^admin/round/(?P<round_seq>\d+)/standings/reply/$', 'reply_standings', name='reply_standings'),
    url(r'^admin/round/(?P<round_seq>\d+)/standings/team/print/$', 'team_standings', { 'for_print': True }, name='team_standings_print'),
    url(r'^admin/round/(?P<round_seq>\d+)/standings/speaker/print/$', 'speaker_standings', { 'for_print': True }, name='speaker_standings_print'),
    url(r'^admin/round/(?P<round_seq>\d+)/standings/reply/print/$', 'reply_standings', { 'for_print': True }, name='reply_standings_print'),
    url(r'^admin/round/(?P<round_seq>\d+)/standings/motions/$', 'motion_standings', name='motion_standings'),
    url(r'^admin/standings/feedback_progress/$', 'feedback_progress', name='feedback_progress'),

    url(r'^admin/ballots/(?P<ballotsub_id>\d+)/edit/$', 'edit_ballotset', name='edit_ballotset'),
    url(r'^admin/debate/(?P<debate_id>\d+)/new_ballotset/$', 'new_ballotset', name='new_ballotset'),
    url(r'^admin/round/(?P<round_seq>\d+)/ballot_checkin/$', 'ballot_checkin', name='ballot_checkin'),
    url(r'^admin/round/(?P<round_seq>\d+)/ballot_checkin/get_details/$', 'ballot_checkin_get_details', name='ballot_checkin_get_details'),
    url(r'^admin/round/(?P<round_seq>\d+)/ballot_checkin/post/$', 'post_ballot_checkin', name='post_ballot_checkin'),

    url(r'^admin/round/(?P<round_seq>\d+)/adjudicators/conflicts/$', 'adj_conflicts', name='adj_conflicts'),
    url(r'^admin/round/(?P<round_seq>\d+)/master_sheets/list/$', 'master_sheets_list', name='master_sheets_list'),
    url(r'^admin/round/(?P<round_seq>\d+)/master_sheets/venue_group/(?P<venue_group_id>\d+)/$', 'master_sheets_view', name='master_sheets_view'),

    url(r'^admin/adjudicators/scores/$', 'adj_scores', name='adj_scores'),
    url(r'^admin/adjudicators/feedback/$', 'adj_feedback', name='adj_feedback'),
    url(r'^admin/adjudicators/feedback/latest/$', 'adj_latest_feedback', name='adj_latest_feedback'),
    url(r'^admin/adjudicators/feedback/source/list/$', 'adj_source_feedback', name='adj_source_feedback'),
    url(r'^admin/adjudicators/feedback/source/team/(?P<team_id>\d+)/$', 'team_feedback_list', name='team_feedback_list'),
    url(r'^admin/adjudicators/feedback/source/adjudicator(?P<adj_id>\d+)/$', 'adj_feedback_list', name='adj_feedback_list'),

    url(r'^admin/adjudicators/feedback/get/$', 'get_adj_feedback', name='get_adj_feedback'),
    url(r'^admin/adjudicators/feedback/add/$', 'add_feedback', name='add_feedback'),
    url(r'^admin/adjudicators/feedback/add/team/(?P<source_id>\d+)/$', 'enter_feedback', {'source_type': m.Team}, name='enter_feedback_team'),
    url(r'^admin/adjudicators/feedback/add/adjudicator/(?P<source_id>\d+)/$', 'enter_feedback', {'source_type': m.Adjudicator}, name='enter_feedback_adjudicator'),
    url(r'^admin/adjudicators/scores/test/set/$', 'set_adj_test_score', name='set_adj_test_score'),
    url(r'^admin/adjudicators/breaking/set/$', 'set_adj_breaking_status', name='set_adj_breaking_status'),
    url(r'^admin/adjudicators/notes/test/set/$', 'set_adj_note', name='set_adj_note'),

    url(r'^admin/break/teams/(?P<category>\w+)/$', 'breaking_teams', name='breaking_teams'),
    url(r'^admin/break/generate/(?P<category>\w+)/$', 'generate_breaking_teams', name='generate_breaking_teams'),
    url(r'^admin/break/eligibility/$', 'break_eligibility', name='break_eligibility'),
    url(r'^admin/break/adjudicators/$',  'breaking_adjs', name='breaking_adjs'),

    url(r'^admin/side_allocations/$', 'side_allocations', name='side_allocations'),
    url(r'^admin/randomised_urls/$', 'randomised_urls', name='randomised_urls'),
    url(r'^admin/randomised_urls/generate/$', 'generate_randomised_urls', name='generate_randomised_urls'),

    url(r'^admin/division_allocations/$', 'division_allocations', name='division_allocations'),
    url(r'^admin/division_allocations/save/$', 'save_divisions', name='save_divisions'),
    url(r'^admin/division_allocations/create/$', 'create_division_allocation', name='create_division_allocation'),

    url(r'^all_tournaments_all_venues/$', 'all_tournaments_all_venues', name='all_tournaments_all_venues'),
    url(r'^all_tournaments_all_venues/all_draws/(?P<venue_id>\d+)$', 'all_draws_for_venue', name='all_draws_for_venue'),
    url(r'^all_tournaments_all_institutions/$', 'all_tournaments_all_institutions', name='all_tournaments_all_institutions'),
    url(r'^all_tournaments_all_institutions/all_draws/(?P<institution_id>\d+)$', 'all_draws_for_institution', name='all_draws_for_institution'),
    url(r'^all_tournaments_all_teams/$', 'all_tournaments_all_teams', name='all_tournaments_all_teams'),

)