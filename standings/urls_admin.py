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

    url(r'^speaker-old/$',  views.speaker_standings,               name='standings-speaker-old'),
    url(r'^novices-old/$',  views.novice_standings,                name='standings-novice-old'),
    url(r'^pros-old/$',     views.pro_standings,                   name='standings-pro-old'),
    url(r'^reply-old/$',    views.reply_standings,                 name='standings-reply-old'),
]
