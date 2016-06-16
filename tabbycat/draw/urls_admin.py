from django.conf.urls import url

from . import views

urlpatterns = [

    # Display
    url(r'^round/(?P<round_seq>\d+)/$',
        views.draw,
        name='draw'),
    url(r'^round/(?P<round_seq>\d+)/details/$',
        views.draw_with_standings,
        name='draw_with_standings'),
    url(r'^round/(?P<round_seq>\d+)/display_by_venue/$',
        views.AdminDrawForRoundByVenue.as_view(),
        name='draw_display_by_venue'),
    url(r'^round/(?P<round_seq>\d+)/display_by_team/$',
        views.AdminDrawForRoundByTeam.as_view(),
        name='draw_display_by_team'),


    # Print
    url(r'^round/(?P<round_seq>\d+)/print/scoresheets/$',
        views.PrintScoreSheetsView.as_view(),
        name='draw_print_scoresheets'),
    url(r'^round/(?P<round_seq>\d+)/print/feedback/$',
        views.PrintFeedbackFormsView.as_view(),
        name='draw_print_feedback'),
    url(r'^round/(?P<round_seq>\d+)/master_sheets/list/$',
        views.master_sheets_list,
        name='master_sheets_list'),
    url(r'^round/(?P<round_seq>\d+)/master_sheets/venue_group/(?P<venue_group_id>\d+)/$',
        views.master_sheets_view,
        name='master_sheets_view'),
    url(r'^round/(?P<round_seq>\d+)/room_sheets_view/venue_group/(?P<venue_group_id>\d+)/$',
        views.room_sheets_view,
        name='room_sheets_view'),

    # Creation/Release
    url(r'^round/(?P<round_seq>\d+)/create/$',
        views.CreateDrawView.as_view(),
        name='create_draw'),
    url(r'^round/(?P<round_seq>\d+)/confirm/$',
        views.confirm_draw,
        name='confirm_draw'),
    url(r'^round/(?P<round_seq>\d+)/confirm_regenerate/$',
        views.draw_confirm_regenerate,
        name='draw_confirm_regenerate'),
    url(r'^round/(?P<round_seq>\d+)/regenerate/$',
        views.draw_regenerate,
        name='draw_regenerate'),
    url(r'^round/(?P<round_seq>\d+)/release/$',
        views.release_draw,
        name='release_draw'),
    url(r'^round/(?P<round_seq>\d+)/unrelease/$',
        views.unrelease_draw,
        name='unrelease_draw'),

    # Side Editing
    url(r'^sides/$',
        views.SideAllocationsView.as_view(),
        name='draw-side-allocations'),
    url(r'^round/(?P<round_seq>\d+)/matchups/edit/$',
        views.draw_matchups_edit,
        name='draw_matchups_edit'),
    url(r'^round/(?P<round_seq>\d+)/matchups/save/$',
        views.save_matchups,
        name='save_matchups'),

    # Scheduling
    url(r'^round/(?P<round_seq>\d+)/schedule_debates/$',
        views.schedule_debates,
        name='schedule_debates'),
    url(r'^round/(?P<round_seq>\d+)/schedule_debates/save/$',
        views.apply_schedule,
        name='apply_schedule'),
    url(r'^round/(?P<round_seq>\d+)/start_time/set/$',
        views.SetRoundStartTimeView.as_view(),
        name='set_round_start_time'),
    url(r'^round/(?P<round_seq>\d+)/confirms/$',
        views.confirmations_view,
        name='confirmations_view'),
]
