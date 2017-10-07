from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    url(r'^current-standings/$',
        views.PublicCurrentTeamStandingsView.as_view(),
        name='standings-public-teams-current'),

    # Transitional provision added 7/10/2017, remove after 7/11/2017
    url(r'^current_standings/$',
        RedirectView.as_view(url='/%(tournament_slug)s/tab/current-standings/', permanent=True)),

    url(r'^team/$',
        views.PublicTeamTabView.as_view(),
        name='standings-public-tab-team'),
    url(r'^speaker/$',
        views.PublicSpeakerTabView.as_view(),
        name='standings-public-tab-speaker'),
    url(r'^speaker/(?P<category>\w+)/$',
        views.PublicSpeakerCategoryTabView.as_view(),
        name='standings-public-tab-speaker-category'),

    url(r'^replies/$',
        views.PublicReplyTabView.as_view(),
        name='standings-public-tab-replies'),
    url(r'^motions/$',
        views.PublicMotionsTabView.as_view(),
        name='standings-public-tab-motions'),

    url(r'^adjudicators/$',
        views.PublicAdjudicatorsTabView.as_view(),
        name='standings-public-adjudicators-tab'),
    url(r'^diversity/$',
        views.PublicDiversityStandingsView.as_view(),
        name='standings-public-diversity'),
]
