from django.urls import path

from . import views

urlpatterns = [
    path('',
        views.PublicBreakIndexView.as_view(),
        name='breakqual-public-index'),
    path('teams/<slug:category>/',
        views.PublicBreakingTeamsView.as_view(),
        name='breakqual-public-teams'),
    path('adjudicators/',
        views.PublicBreakingAdjudicatorsView.as_view(),
        name='breakqual-public-adjs'),
]
