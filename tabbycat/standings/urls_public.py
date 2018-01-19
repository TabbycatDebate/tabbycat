from django.urls import path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('current-standings/',
        views.PublicCurrentTeamStandingsView.as_view(),
        name='standings-public-teams-current'),

    # Transitional provision added 7/10/2017, remove after 7/11/2017
    path('current_standings/',
        RedirectView.as_view(url='/%(tournament_slug)s/tab/current-standings/', permanent=True)),

    path('team/',
        views.PublicTeamTabView.as_view(),
        name='standings-public-tab-team'),
    path('speaker/',
        views.PublicSpeakerTabView.as_view(),
        name='standings-public-tab-speaker'),
    path('speaker/<slug:category>/',
        views.PublicSpeakerCategoryTabView.as_view(),
        name='standings-public-tab-speaker-category'),

    path('replies/',
        views.PublicReplyTabView.as_view(),
        name='standings-public-tab-replies'),
    path('motions/',
        views.PublicMotionsTabView.as_view(),
        name='standings-public-tab-motions'),

    path('adjudicators/',
        views.PublicAdjudicatorsTabView.as_view(),
        name='standings-public-adjudicators-tab'),
    path('diversity/',
        views.PublicDiversityStandingsView.as_view(),
        name='standings-public-diversity'),
]
