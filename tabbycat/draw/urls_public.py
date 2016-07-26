from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',
        views.PublicDrawForCurrentRoundView.as_view(),
        name='draw-public-current-round'),
    url(r'^round/(?P<round_seq>\d+)/$',
        views.PublicDrawForRoundView.as_view(),
        name='draw-public-draw-round'),
    url(r'^all/$',
        views.PublicAllDrawsAllTournamentsView.as_view(),
        name='draw-public-all-draws'),
    url(r'^sides/$',
        views.PublicSideAllocationsView.as_view(),
        name='draw-public-side-allocations'),
]
