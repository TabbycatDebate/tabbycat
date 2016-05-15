from django.conf.urls import *

from . import views

urlpatterns = [
    url(r'^list/$',
        views.PublicDrawForRound.as_view(),
        name='public_participants'),
    url(r'^team_list/(?P<team_id>\d+)/$',
        views.team_speakers,
        name='team_speakers'),
    url(r'^all_tournaments_all_teams/$',
        views.all_tournaments_all_teams,
        name='all_tournaments_all_teams'),
    url(r'^all_tournaments_all_institutions/$',
        views.all_tournaments_all_institutions,
        name='all_tournaments_all_institutions'),

    url(r'^shifts/a(?P<url_key>\w+)/$',
        views.public_confirm_shift_key,
        name='public_confirm_shift_key'),
]
