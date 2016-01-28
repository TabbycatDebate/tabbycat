from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$',          views.standings_index,      name='standings_index'),
    url(r'^team/$',     views.team_standings,       name='team_standings'),
    url(r'^division/$', views.division_standings,   name='division_standings'),
    url(r'^speaker/$',  views.speaker_standings,    name='speaker_standings'),
    url(r'^novices/$',  views.novice_standings,     name='novice_standings'),
    url(r'^reply/$',    views.reply_standings,      name='reply_standings'),
    url(r'^motions/$',  views.motion_standings,     name='motion_standings'),

]