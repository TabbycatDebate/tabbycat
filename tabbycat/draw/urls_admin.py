from django.urls import include, path

from . import views

urlpatterns = [

    path('round/<int:round_seq>/', include([
        # Creation/Release
        path('',
            views.AdminDrawView.as_view(),
            name='draw'),
        path('create/',
            views.CreateDrawView.as_view(),
            name='draw-create'),
        path('details/',
            views.AdminDrawWithDetailsView.as_view(),
            name='draw-details'),
        path('position-balance/',
            views.PositionBalanceReportView.as_view(),
            name='draw-position-balance'),
        path('confirm/',
            views.ConfirmDrawCreationView.as_view(),
            name='draw-confirm'),
        path('regenerate/confirm/',
            views.ConfirmDrawRegenerationView.as_view(),
            name='draw-confirm-regenerate'),
        path('regenerate/',
            views.DrawRegenerateView.as_view(),
            name='draw-regenerate'),

        # Email
        path('email-adjudicators',
            views.EmailAdjudicatorAssignmentsView.as_view(),
            name='draw-adj-email'),
        path('email-debaters',
            views.EmailTeamAssignmentsView.as_view(),
            name='draw-team-email'),

        # Side and Matchup Editing
        path('edit/',
            views.EditDebateTeamsView.as_view(),
            name='edit-debate-teams'),
        path('matchups/edit/',
            views.LegacyEditMatchupsView.as_view(),
            name='legacy-draw-matchups-edit'),
        path('matchups/save/',
            views.LegacySaveDrawMatchupsView.as_view(),
            name='legacy-save-debate-teams'),
        path('sides/save/',
            views.LegacySaveDebateSidesStatusView.as_view(),
            name='legacy-save-debate-sides-status'),

        # Display
        path('display/',
            views.AdminDrawDisplayView.as_view(),
            name='draw-display'),
        path('display-by-venue/',
            views.AdminDrawDisplayForSpecificRoundByVenueView.as_view(),
            name='draw-display-specific-round-by-venue'),
        path('display-by-team/',
            views.AdminDrawDisplayForSpecificRoundByTeamView.as_view(),
            name='draw-display-specific-round-by-team'),
        path('release/',
            views.DrawReleaseView.as_view(),
            name='draw-release'),
        path('unrelease/',
            views.DrawUnreleaseView.as_view(),
            name='draw-unrelease'),

        # Scheduling
        path('schedule/',
            views.ScheduleDebatesView.as_view(),
            name='draw-schedule-debates'),
        path('schedule/save/',
            views.ApplyDebateScheduleView.as_view(),
            name='draw-schedule-apply'),
        path('confirms/',
            views.ScheduleConfirmationsView.as_view(),
            name='draw-schedule-confirmations'),
        path('start-time/set/',
            views.SetRoundStartTimeView.as_view(),
            name='draw-start-time-set'),
    ])),

    path('round/current/display-by-venue/',
        views.AdminDrawDisplayForCurrentRoundsByVenueView.as_view(),
        name='draw-display-current-rounds-by-venue'),
    path('round/current/display-by-team/',
        views.AdminDrawDisplayForCurrentRoundsByTeamView.as_view(),
        name='draw-display-current-rounds-by-team'),

    path('sides/',
        views.SideAllocationsView.as_view(),
        name='draw-side-allocations'),

]
