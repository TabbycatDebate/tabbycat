from django.urls import path

from . import views

urlpatterns = [
    path('',
        views.PublicBreakIndexView.as_view(),
        name='breakqual-public-index'),
    path('teams/<slug:category>/',
        views.PublicBreakingTeamsView.as_view(),
        name='breakqual-public-teams'),
    path('bracket/<slug:category>/',
        views.PublicEliminationBracketView.as_view(),
        name='breakqual-public-bracket'),
    path('adjudicators/',
        views.PublicBreakingAdjudicatorsView.as_view(),
        name='breakqual-public-adjs'),
]
