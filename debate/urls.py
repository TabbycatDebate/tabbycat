from django.conf.urls import *

from django.core.urlresolvers import reverse

from debate import models as m

urlpatterns = patterns('debate.views',
    url(r'^admin/$', 'tournament_home', name='tournament_home'),
    url(r'^admin/draw/$', 'draw_index', name='draw_index'),
    url(r'^admin/round/(?P<round_seq>\d+)/$', 'round_index', name='round_index'),

    url(r'^$', 'public_index', name='public_index'),
    url(r'^draw/$', 'public_draw', name='public_draw'),
    url(r'^draw/round/(?P<round_seq>\d+)/$', 'public_draw_by_round', name='public_draw_by_round'),
    url(r'^draw/all/$', 'public_all_draws', name='public_all_draws'),


    url(r'^standings/$',    'public_team_standings', name='public_team_standings'),

    url(r'^team_speakers/(?P<team_id>\d+)/$', 'team_speakers', name='team_speakers'),



    url(r'^toggle_postponed/$', 'toggle_postponed', name='toggle_postponed'),




    url(r'^participants/$', 'public_participants', name='public_participants'),
    url(r'^motions/$', 'public_motions', name='public_motions'),
    url(r'^divisions/$', 'public_divisions', name='public_divisions'),
    url(r'^side_allocations/$', 'public_side_allocations', name='public_side_allocations'),


    #url(r'^admin/actions/$', 'action_log', name='action_log'),

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

    url(r'^admin/round/(?P<round_seq>\d+)/draw/adjudicators/$', 'draw_adjudicators_edit', name='draw_adjudicators_edit'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/adjudicators/_get/$', 'draw_adjudicators_get', name='draw_adjudicators_get'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/adjudicators/save/$', 'save_adjudicators', name='save_adjudicators'),
    url(r'^admin/round/(?P<round_seq>\d+)/_update_importance/$', 'update_debate_importance', name='update_debate_importance'),


    url(r'^admin/round/(?P<round_seq>\d+)/round_increment_check/$', 'round_increment_check', name='round_increment_check'),
    url(r'^admin/round/(?P<round_seq>\d+)/round_increment/$', 'round_increment', name='round_increment'),

    url(r'^admin/round/(?P<round_seq>\d+)/adj_allocation/create/$', 'create_adj_allocation', name='create_adj_allocation'),
    url(r'^admin/round/(?P<round_seq>\d+)/start_time/set/$', 'set_round_start_time', name='set_round_start_time'),


    url(r'^admin/round/(?P<round_seq>\d+)/adjudicators/conflicts/$', 'adj_conflicts', name='adj_conflicts'),
    url(r'^admin/round/(?P<round_seq>\d+)/master_sheets/list/$', 'master_sheets_list', name='master_sheets_list'),
    url(r'^admin/round/(?P<round_seq>\d+)/master_sheets/venue_group/(?P<venue_group_id>\d+)/$', 'master_sheets_view', name='master_sheets_view'),

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

    # Printing App
    url(r'^admin/print/round/(?P<round_seq>\d+)/',          include('printing.urls')),

    # Standings App
    url(r'^tab/',                                           include('standings.urls_public')),
    url(r'^admin/standings/round/(?P<round_seq>\d+)/',      include('standings.urls_admin')),

    # Break App
    url(r'^break/',                                         include('breaking.urls_public')),
    url(r'^admin/break/',                                   include('breaking.urls_admin')),

    # Availability App
    url(r'^admin/availability/round/(?P<round_seq>\d+)/',   include('availability.urls')),

    # Motions App
    url(r'^admin/motions/round/(?P<round_seq>\d+)/',        include('motions.urls')),

    # Action Log App
    url(r'^admin/action_log/',                              include('action_log.urls')),

    # Config App
    url(r'^admin/options/',                                 include('options.urls')),

    # Feedback App
    url(r'^feedback/',                                      include('feedback.urls_public')),
    url(r'^admin/feedback/',                                include('feedback.urls_admin')),

    # Results App
    url(r'^results/',                                       include('results.urls_public')),
    url(r'^admin/results/',                                 include('results.urls_admin')),





)