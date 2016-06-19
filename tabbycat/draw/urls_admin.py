from django.conf.urls import url

from . import views

urlpatterns = [

    # Display
    url(r'^round/(?P<round_seq>\d+)/$',
        views.AdminDrawEditView.as_view(),
        name='draw'),
    url(r'^round/(?P<round_seq>\d+)/details/$',
        views.AdminDrawWithDetailsView.as_view(),
        name='draw_with_standings'),
    url(r'^round/(?P<round_seq>\d+)/display_by_venue/$',
        views.AdminDrawDisplayForRoundByVenue.as_view(),
        name='draw_display_by_venue'),
    url(r'^round/(?P<round_seq>\d+)/display_by_team/$',
        views.AdminDrawDisplayForRoundByTeam.as_view(),
        name='draw_display_by_team'),

    # Creation/Release
    url(r'^round/(?P<round_seq>\d+)/create/$',
        views.CreateDrawView.as_view(),
        name='create_draw'),
    url(r'^round/(?P<round_seq>\d+)/confirm/$',
        views.ConfirmDrawCreationView.as_view(),
        name='confirm_draw'),
    url(r'^round/(?P<round_seq>\d+)/confirm_regenerate/$',
        views.ConfirmDrawRegenerationView.as_view(),
        name='draw_confirm_regenerate'),
    url(r'^round/(?P<round_seq>\d+)/regenerate/$',
        views.DrawRegenerateView.as_view(),
        name='draw_regenerate'),
    url(r'^round/(?P<round_seq>\d+)/release/$',
        views.DrawReleaseView.as_view(),
        name='release_draw'),
    url(r'^round/(?P<round_seq>\d+)/unrelease/$',
        views.DrawUnreleaseView.as_view(),
        name='unrelease_draw'),

    # Side Editing
    url(r'^sides/$',
        views.SideAllocationsView.as_view(),
        name='draw-side-allocations'),
    url(r'^round/(?P<round_seq>\d+)/matchups/edit/$',
        views.DrawMatchupsEditView.as_view(),
        name='draw_matchups_edit'),
    url(r'^round/(?P<round_seq>\d+)/matchups/save/$',
        views.SaveDrawMatchups.as_view(),
        name='save_matchups'),

    # Scheduling
    url(r'^round/(?P<round_seq>\d+)/schedule_debates/$',
        views.ScheduleDebatesView.as_view(),
        name='schedule_debates'),
    url(r'^round/(?P<round_seq>\d+)/schedule_debates/save/$',
        views.ApplyDebateSchedyleView.as_view(),
        name='apply_schedule'),
    url(r'^round/(?P<round_seq>\d+)/confirms/$',
        views.ScheduleConfirmationsView.as_view(),
        name='confirmations_view'),

    url(r'^round/(?P<round_seq>\d+)/start_time/set/$',
        views.SetRoundStartTimeView.as_view(),
        name='set_round_start_time'),
]
