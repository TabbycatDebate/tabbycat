from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',          views.standings_index,                 name='standings-index'),
    url(r'^team/$',     views.TeamStandingsView.as_view(),     name='standings-team'),
    url(r'^division/$', views.DivisionStandingsView.as_view(), name='standings-division'),

    url(r'^speaker/$',  views.speaker_standings,               name='standings-speaker'),
    url(r'^novices/$',  views.novice_standings,                name='standings-novice'),
    url(r'^novices/$',  views.pro_standings,                   name='standings-pro'),
    url(r'^reply/$',    views.reply_standings,                 name='standings-reply'),
    url(r'^motions/$',  views.motion_standings,                name='standings-motion'),

]
