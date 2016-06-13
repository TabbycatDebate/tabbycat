from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$',
        views.public_index,
        name='tournament-public-index'),
    url(r'^admin/overview/$',
        views.TournamentAdminHomeView.as_view(),
        name='tournament-admin-home'),

    # TODO: 'core' app functionality?
    url(r'^admin/round/(?P<round_seq>\d+)/round_increment_check/$',
        views.round_increment_check,
        name='round_increment_check'),
    url(r'^admin/round/(?P<round_seq>\d+)/round_increment/$',
        views.round_increment,
        name='round_increment'),

    # Divisions Specific
    url(r'^divisions/$',
        views.public_divisions,
        name='public_divisions'),
    url(r'^admin/divisions/allocate/$',
        views.division_allocations,
        name='division_allocations'),
    # POST METHODS
    url(r'^admin/divisions/set_venue_group/$',
        views.set_division_venue_group,
        name='set_division_venue_group'),
    url(r'^admin/divisions/set_team/$',
        views.set_team_division,
        name='set_team_division'),
    url(r'^admin/divisions/set_time/$',
        views.set_division_time,
        name='set_division_time'),
    # MANUAL ACTIONS
    url(r'^admin/divisions/create/$',
        views.create_division,
        name='create_division'),
    url(r'^admin/divisions/create_division_allocation/$',
        views.create_division_allocation,
        name='create_division_allocation'),
    url(r'^admin/divisions/create_byes/$',
        views.create_byes,
        name='create_byes'),

    # WADL-specific; unclear if draws or participants
    url(r'^all_tournaments_all_venues/$',
        views.all_tournaments_all_venues,
        name='all_tournaments_all_venues'),
    url(r'^all_tournaments_all_venues/all_draws/(?P<venue_id>\d+)$',
        views.all_draws_for_venue,
        name='all_draws_for_venue'),
    url(r'^all_tournaments_all_institutions/all_draws/(?P<institution_id>\d+)$',
        views.all_draws_for_institution,
        name='all_draws_for_institution'),

    # Action Logs App
    url(r'^admin/action_log/', include('actionlog.urls')),

    # Allocations App
    url(r'^admin/allocations/round/(?P<round_seq>\d+)/',
        include('adjallocation.urls')),

    # Availabilities App
    url(r'^admin/availability/round/(?P<round_seq>\d+)/',
        include('availability.urls')),

    # Breaks App
    url(r'^break/', include('breakqual.urls_public')),
    url(r'^admin/break/', include('breakqual.urls_admin')),

    # Draws App
    url(r'^draw/', include('draw.urls_public')),
    url(r'^admin/draw/', include('draw.urls_admin')),

    # Feedbacks App
    url(r'^feedback/', include('adjfeedback.urls_public')),
    url(r'^admin/feedback/', include('adjfeedback.urls_admin')),

    # Importer App
    url(r'^admin/import/', include('importer.urls')),

    # Motions App
    url(r'^motions/', include('motions.urls_public')),
    url(r'^admin/motions/round/(?P<round_seq>\d+)/',
        include('motions.urls_admin')),

    # Options App
    url(r'^admin/options/', include('options.urls')),

    # Participants App
    url(r'^participants/', include('participants.urls_public')),
    url(r'^admin/participants/', include('participants.urls_admin')),

    # Results App
    url(r'^results/', include('results.urls_public')),
    url(r'^admin/results/', include('results.urls_admin')),

    # Standings App
    url(r'^standings/', include('standings.urls_public')),
    url(r'^tab/', include('standings.urls_public')),
    url(r'^admin/standings/round/(?P<round_seq>\d+)/',
        include('standings.urls_admin')),

    # Venues App
    url(r'^admin/venues/', include('venues.urls_admin')),
]
