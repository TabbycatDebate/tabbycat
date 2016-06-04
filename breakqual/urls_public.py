from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',
        views.public_break_index,
        name='public_break_index'),
    url(r'^teams/(?P<category>\w+)/$',
        views.PublicBreakingTeams.as_view(),
        name='public_breaking_teams'),
    url(r'^adjudicators/$',
        views.PublicBreakingAdjudicators.as_view(),
        name='public_breaking_adjs'),
]
