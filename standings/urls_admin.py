from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',          views.standings_index,                 name='standings-index'),
    url(r'^team/$',     views.TeamStandingsView.as_view(),     name='standings-team'),
    url(r'^division/$', views.DivisionStandingsView.as_view(), name='standings-division'),

    url(r'^speaker/$',  views.SpeakerStandingsView.as_view(),  name='standings-speaker'),
    url(r'^novices/$',  views.NoviceStandingsView.as_view(),   name='standings-novice'),
    url(r'^pros/$',     views.ProStandingsView.as_view(),      name='standings-pro'),
    url(r'^reply/$',    views.ReplyStandingsView.as_view(),    name='standings-reply'),
    url(r'^motions/$',  views.motion_standings,                name='standings-motion'),
]
