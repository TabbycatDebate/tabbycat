from django.conf.urls import include, url

from . import views

urlpatterns = [

    url(r'^$',
        views.TournamentPublicHomeView.as_view(),
        name='tournament-public-index'),
    url(r'^admin/$',
        views.TournamentAdminHomeView.as_view(),
        name='tournament-admin-home'),

    # Application URLs for public pages
    url(r'^break/',              include('breakqual.urls_public')),
    url(r'^divisions/',          include('divisions.urls')),
    url(r'^draw/',               include('draw.urls_public')),
    url(r'^feedback/',           include('adjfeedback.urls_public')),
    url(r'^motions/',            include('motions.urls_public')),
    url(r'^participants/',       include('participants.urls_public')),
    url(r'^results/',            include('results.urls_public')),
    url(r'^standings/',          include('standings.urls_public')),
    url(r'^tab/',                include('standings.urls_public')),

    # Application URLs for admin pages
    url(r'^admin/actionlog/',    include('actionlog.urls')),
    url(r'^admin/allocations/',  include('adjallocation.urls')),
    url(r'^admin/availability/', include('availability.urls')),
    url(r'^admin/break/',        include('breakqual.urls_admin')),
    url(r'^admin/draw/',         include('draw.urls_admin')),
    url(r'^admin/feedback/',     include('adjfeedback.urls_admin')),
    url(r'^admin/import/',       include('importer.urls')),
    url(r'^admin/motions/',      include('motions.urls_admin')),
    url(r'^admin/options/',      include('options.urls')),
    url(r'^admin/participants/', include('participants.urls_admin')),
    url(r'^admin/printing/',     include('printing.urls_admin')),
    url(r'^admin/privateurls/',  include('privateurls.urls')),
    url(r'^admin/results/',      include('results.urls_admin')),
    url(r'^admin/standings/',    include('standings.urls_admin')),
    url(r'^admin/venues/',       include('venues.urls_admin')),

    # Round progression
    url(r'^admin/round/(?P<round_seq>\d+)/advance/check/$',
        views.RoundAdvanceConfirmView.as_view(),
        name='tournament-advance-round-check'),
    url(r'^admin/round/(?P<round_seq>\d+)/advance/$',
        views.RoundAdvanceView.as_view(),
        name='tournament-advance-round'),
    url(r'^admin/set-current-round/$',
        views.SetCurrentRoundView.as_view(),
        name='tournament-set-current-round'),

    # Other pages
    url(r'^admin/configure/$',
        views.ConfigureTournamentView.as_view(),
        name='tournament-configure'),
    url(r'^admin/fix-debate-teams/$',
        views.FixDebateTeamsView.as_view(),
        name='tournament-fix-debate-teams'),
    url(r'^donations/$',
        views.TournamentDonationsView.as_view(),
        name='tournament-donations'),
]
