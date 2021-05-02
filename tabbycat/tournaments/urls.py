from django.urls import include, path

from . import views

urlpatterns = [

    path('',
        views.TournamentPublicHomeView.as_view(),
        name='tournament-public-index'),
    path('admin/',
        views.TournamentAdminHomeView.as_view(),
        name='tournament-admin-home'),
    path('assistant/',
        views.TournamentAssistantHomeView.as_view(),
        name='tournament-assistant-home'),

    # Application URLs for public pages
    path('break/',                  include('breakqual.urls_public')),
    path('checkins/',               include('checkins.urls_public')),
    path('draw/',                   include('draw.urls_public')),
    path('feedback/',               include('adjfeedback.urls_public')),
    path('motions/',                include('motions.urls_public')),
    path('participants/',           include('participants.urls_public')),
    path('privateurls/',            include('privateurls.urls_public')),
    path('results/',                include('results.urls_public')),
    path('standings/',              include('standings.urls_public')),
    path('tab/',                    include('standings.urls_public')),

    # Application URLs for admin pages
    path('admin/allocations/',      include('adjallocation.urls')),
    path('admin/availability/',     include('availability.urls')),
    path('admin/break/',            include('breakqual.urls_admin')),
    path('admin/checkins/',         include('checkins.urls_admin')),
    path('admin/draw/',             include('draw.urls_admin')),
    path('admin/feedback/',         include('adjfeedback.urls_admin')),
    path('admin/import/',           include('importer.urls')),
    path('admin/motions/',          include('motions.urls_admin')),
    path('admin/notifications/',    include('notifications.urls_admin')),
    path('admin/options/',          include('options.urls')),
    path('admin/participants/',     include('participants.urls_admin')),
    path('admin/printing/',         include('printing.urls_admin')),
    path('admin/privateurls/',      include('privateurls.urls_admin')),
    path('admin/results/',          include('results.urls_admin')),
    path('admin/standings/',        include('standings.urls_admin')),
    path('admin/venues/',           include('venues.urls_admin')),

    # Application URLs for assistant pages
    path('assistant/feedback/',     include('adjfeedback.urls_assistant')),
    path('assistant/checkins/',     include('checkins.urls_assistant')),
    path('assistant/draw/',         include('draw.urls_assistant')),
    path('assistant/motions/',      include('motions.urls_assistant')),
    path('assistant/participants/', include('participants.urls_assistant')),
    path('assistant/printing/',     include('printing.urls_assistant')),
    path('assistant/results/',      include('results.urls_assistant')),

    # Round progression
    path('admin/round/<int:round_seq>/complete/check/',
        views.CompleteRoundCheckView.as_view(),
        name='tournament-complete-round-check'),
    path('admin/round/<int:round_seq>/complete/',
        views.CompleteRoundView.as_view(),
        name='tournament-complete-round'),
    path('admin/set-current-round/',
        views.SetCurrentRoundView.as_view(),
        name='tournament-set-current-round'),

    # Other pages
    path('admin/configure/',
        views.ConfigureTournamentView.as_view(),
        name='tournament-configure'),
    path('admin/fix-debate-teams/',
        views.FixDebateTeamsView.as_view(),
        name='tournament-fix-debate-teams'),
    path('donations/',
        views.TournamentDonationsView.as_view(),
        name='tournament-donations'),
]
