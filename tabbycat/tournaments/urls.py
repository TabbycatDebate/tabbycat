from django.conf.urls import include, url

from . import views

urlpatterns = [

    url(r'^$',
        views.TournamentPublicHomeView.as_view(),
        name='tournament-public-index'),
    url(r'^admin/overview/$',
        views.TournamentAdminHomeView.as_view(),
        name='tournament-admin-home'),

    url(r'^admin/round/(?P<round_seq>\d+)/round_increment_check/$',
        views.RoundIncrementConfirmView.as_view(),
        name='round_increment_check'),
    url(r'^admin/round/(?P<round_seq>\d+)/round_increment/$',
        views.RoundIncrementView.as_view(),
        name='round_increment'),

    # Action Logs App
    url(r'^admin/action_log/',
        include('actionlog.urls')),

    # Allocations App
    url(r'^admin/allocations/round/(?P<round_seq>\d+)/',
        include('adjallocation.urls')),

    # Availabilities App
    url(r'^admin/availability/round/(?P<round_seq>\d+)/',
        include('availability.urls')),

    # Breaks App
    url(r'^break/',
        include('breakqual.urls_public')),
    url(r'^admin/break/',
        include('breakqual.urls_admin')),

    # Divisions App
    url(r'^divisions/',
        include('divisions.urls')),

    # Draws App
    url(r'^draw/',
        include('draw.urls_public')),
    url(r'^admin/draw/',
        include('draw.urls_admin')),

    # Feedbacks App
    url(r'^feedback/',
        include('adjfeedback.urls_public')),
    url(r'^admin/feedback/',
        include('adjfeedback.urls_admin')),

    # Importer App
    url(r'^admin/import/',
        include('importer.urls')),

    # Motions App
    url(r'^motions/',
        include('motions.urls_public')),
    url(r'^admin/motions/round/(?P<round_seq>\d+)/',
        include('motions.urls_admin')),

    # Options App
    url(r'^admin/options/',
        include('options.urls')),

    # Printing App
    url(r'^admin/printing/',
        include('printing.urls_admin')),

    # Participants App
    url(r'^participants/',
        include('participants.urls_public')),
    url(r'^admin/participants/',
        include('participants.urls_admin')),

    # Results App
    url(r'^results/',
        include('results.urls_public')),
    url(r'^admin/results/',
        include('results.urls_admin')),

    # Standings App
    url(r'^standings/',
        include('standings.urls_public')),
    url(r'^tab/',
        include('standings.urls_public')),
    url(r'^admin/standings/round/(?P<round_seq>\d+)/',
        include('standings.urls_admin')),

    # Venues App
    url(r'^admin/venues/',
        include('venues.urls_admin')),
]
