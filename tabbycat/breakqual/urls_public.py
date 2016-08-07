from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',
        views.PublicBreakIndexView.as_view(),
        name='breakqual-public-index'),
    url(r'^teams/(?P<category>\w+)/$',
        views.PublicBreakingTeamsView.as_view(),
        name='breakqual-public-teams'),
    url(r'^adjudicators/$',
        views.PublicBreakingAdjudicatorsView.as_view(),
        name='breakqual-public-adjs'),
]
