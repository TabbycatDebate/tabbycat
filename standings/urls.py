from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^team/$',     views.team_standings,           name='team_standings'),
    url(r'^division/$', views.division_standings,       name='division_standings'),
    url(r'^speaker/$',  views.speaker_standings,        name='speaker_standings'),
    url(r'^novices/$',  views.novice_standings,         name='novice_standings'),
    url(r'^reply/$',    views.reply_standings,          name='reply_standings'),
    url(r'^motions/$',  views.motion_standings,         name='motion_standings'),

    url(r'^public_team/$',     views.public_team_tab,      name='public_team_tab'),
    url(r'^public_speaker/$',  views.public_speaker_tab,   name='public_speaker_tab'),
    url(r'^public_novices/$',  views.public_novices_tab,   name='public_novices_tab'),
    url(r'^public_replies/$',  views.public_replies_tab,   name='public_replies_tab'),
    url(r'^public_motions/$',  views.public_motions_tab,   name='public_motions_tab'),

]