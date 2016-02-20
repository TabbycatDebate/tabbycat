from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^current/$',  views.public_team_standings,       name='standings-public-teams-current'),
    url(r'^team/$',     views.PublicTeamTabView.as_view(), name='standings-public-tab-team'),
    url(r'^speaker/$',  views.public_speaker_tab,          name='standings-public-tab-speaker'),
    url(r'^novices/$',  views.public_novices_tab,          name='standings-public-tab-novices'),
    url(r'^replies/$',  views.public_replies_tab,          name='standings-public-tab-replies'),
    url(r'^motions/$',  views.public_motions_tab,          name='standings-public-tab-motions'),

]