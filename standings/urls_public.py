from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^current_standings/$',
        views.PublicCurrentTeamStandingsView.as_view(),
        name='standings-public-teams-current'),
    url(r'^team/$',
        views.PublicTeamTabView.as_view(),
        name='standings-public-tab-team'),
    url(r'^speaker/$',
        views.PublicSpeakerTabView.as_view(),
        name='standings-public-tab-speaker'),
    url(r'^pros/$',
        views.PublicProTabView.as_view(),
        name='standings-public-tab-pros'),
    url(r'^novices/$',
        views.PublicNoviceTabView.as_view(),
        name='standings-public-tab-novices'),
    url(r'^replies/$',
        views.PublicReplyTabView.as_view(),
        name='standings-public-tab-replies'),
    url(r'^motions/$',
        views.public_motions_tab,
        name='standings-public-tab-motions'),
]
