from django.urls import path

from . import views

urlpatterns = [

    # Creation/Release
    path('round/<int:round_seq>/',
        views.AdminDrawView.as_view(),
        name='draw'),
    path('round/<int:round_seq>/create/',
        views.CreateDrawView.as_view(),
        name='draw-create'),
    path('round/<int:round_seq>/details/',
        views.AdminDrawWithDetailsView.as_view(),
        name='draw-details'),
    path('round/<int:round_seq>/position-balance/',
        views.PositionBalanceReportView.as_view(),
        name='draw-position-balance'),
    path('round/<int:round_seq>/confirm/',
        views.ConfirmDrawCreationView.as_view(),
        name='draw-confirm'),
    path('round/<int:round_seq>/regenerate/confirm/',
        views.ConfirmDrawRegenerationView.as_view(),
        name='draw-confirm-regenerate'),
    path('round/<int:round_seq>/regenerate/',
        views.DrawRegenerateView.as_view(),
        name='draw-regenerate'),

    # Side Editing
    path('sides/',
        views.SideAllocationsView.as_view(),
        name='draw-side-allocations'),
    path('round/<int:round_seq>/matchups/edit/',
        views.EditMatchupsView.as_view(),
        name='draw-matchups-edit'),
    path('round/<int:round_seq>/matchups/save/',
        views.SaveDrawMatchupsView.as_view(),
        name='save-debate-teams'),
    path('round/<int:round_seq>/sides/save/',
        views.SaveDebateSidesStatusView.as_view(),
        name='save-debate-sides-status'),

    # Display
    path('round/<int:round_seq>/display/',
        views.AdminDrawDisplay.as_view(),
        name='draw-display'),
    path('round/<int:round_seq>/display-by-venue/',
        views.AdminDrawDisplayForRoundByVenueView.as_view(),
        name='draw-display-by-venue'),
    path('round/<int:round_seq>/display-by-team/',
        views.AdminDrawDisplayForRoundByTeamView.as_view(),
        name='draw-display-by-team'),
    path('round/<int:round_seq>/release/',
        views.DrawReleaseView.as_view(),
        name='draw-release'),
    path('round/<int:round_seq>/unrelease/',
        views.DrawUnreleaseView.as_view(),
        name='draw-unrelease'),

    # Scheduling
    path('round/<int:round_seq>/schedule/',
        views.ScheduleDebatesView.as_view(),
        name='draw-schedule-debates'),
    path('round/<int:round_seq>/schedule/save/',
        views.ApplyDebateScheduleView.as_view(),
        name='draw-schedule-apply'),
    path('round/<int:round_seq>/confirms/',
        views.ScheduleConfirmationsView.as_view(),
        name='draw-schedule-confirmations'),
    path('round/<int:round_seq>/start-time/set/',
        views.SetRoundStartTimeView.as_view(),
        name='draw-start-time-set'),

]
