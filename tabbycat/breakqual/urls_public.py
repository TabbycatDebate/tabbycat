from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',
        views.public_break_index,
        name='public_break_index'),
    url(r'^teams/(?P<category>\w+)/$',
        views.PublicBreakingTeamsView.as_view(),
        name='public_breaking_teams'),
    url(r'^adjudicators/$',
        views.PublicBreakingAdjudicatorsView.as_view(),
        name='public_breaking_adjs'),
]
