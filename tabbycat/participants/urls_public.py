from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list/$',
        views.PublicParticipantsListView.as_view(),
        name='participants-public-list'),

    url(r'^team/(?P<pk>\d+)/$',
        views.PublicTeamSummaryView.as_view(),
        name='participants-public-team-summary'),
    url(r'^adjudicator/(?P<pk>\d+)/$',
        views.PublicAdjudicatorSummaryView.as_view(),
        name='participants-public-adjudicator-summary'),

    url(r'^team_list/(?P<team_id>\d+)/$',
        views.TeamSpeakersJsonView.as_view(),
        name='participants-team-speakers'),
    url(r'^all_tournaments_all_teams/$',
        views.AllTournamentsAllTeamsView.as_view(),
        name='participants-all-tournaments-all-teams'),
    url(r'^all_tournaments_all_institutions/$',
        views.AllTournamentsAllInstitutionsView.as_view(),
        name='participants-all-tournaments-all-institutions'),

    url(r'^shifts/a(?P<url_key>\w+)/$',
        views.PublicConfirmShiftView.as_view(),
        name='participants-public-confirm-shift'),
]
