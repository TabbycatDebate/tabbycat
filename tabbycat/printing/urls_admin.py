from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^round/(?P<round_seq>\d+)/print/scoresheets/$',
        views.PrintScoreSheetsView.as_view(),
        name='draw_print_scoresheets'),

    url(r'^round/(?P<round_seq>\d+)/print/feedback/$',
        views.PrintFeedbackFormsView.as_view(),
        name='draw_print_feedback'),

    url(r'^round/(?P<round_seq>\d+)/master_sheets/list/$',
        views.MasterSheetsListView.as_view(),
        name='master_sheets_list'),

    url(r'^round/(?P<round_seq>\d+)/master_sheets/venue_group/(?P<venue_group_id>\d+)/$',
        views.MasterSheetsView.as_view(),
        name='master_sheets_view'),

    url(r'^round/(?P<round_seq>\d+)/room_sheets_view/venue_group/(?P<venue_group_id>\d+)/$',
        views.RoomSheetsView.as_view(),
        name='room_sheets_view'),

]
