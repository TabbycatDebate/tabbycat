from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^current/$',  views.public_team_standings,name='public_team_standings'),

    url(r'^team/$',     views.public_team_tab,      name='public_team_tab'),
    url(r'^speaker/$',  views.public_speaker_tab,   name='public_speaker_tab'),
    url(r'^novices/$',  views.public_novices_tab,   name='public_novices_tab'),
    url(r'^replies/$',  views.public_replies_tab,   name='public_replies_tab'),
    url(r'^motions/$',  views.public_motions_tab,   name='public_motions_tab'),

]