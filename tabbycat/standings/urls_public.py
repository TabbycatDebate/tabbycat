from django.urls import path

from . import views

urlpatterns = [
    path('current-standings/',
        views.PublicCurrentTeamStandingsView.as_view(),
        name='standings-public-teams-current'),

    path('team/',
        views.PublicTeamTabView.as_view(),
        name='standings-public-tab-team'),
    path('team/<slug:category>/',
        views.PublicBreakCategoryTabView.as_view(),
        name='standings-public-tab-break-category'),
    path('speaker/',
        views.PublicSpeakerTabView.as_view(),
        name='standings-public-tab-speaker'),
    path('speaker/<slug:category>/',
        views.PublicSpeakerCategoryTabView.as_view(),
        name='standings-public-tab-speaker-category'),

    path('replies/',
        views.PublicReplyTabView.as_view(),
        name='standings-public-tab-replies'),

    path('adjudicators/',
        views.PublicAdjudicatorsTabView.as_view(),
        name='standings-public-adjudicators-tab'),
    path('diversity/',
        views.PublicDiversityStandingsView.as_view(),
        name='standings-public-diversity'),
]
