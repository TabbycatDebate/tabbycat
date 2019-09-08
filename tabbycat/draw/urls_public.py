from django.urls import path

from . import views

urlpatterns = [
    path('',
        views.PublicDrawForCurrentRoundsView.as_view(),
        name='draw-public-current-rounds'),
    path('round/<int:round_seq>/',
        views.PublicDrawForRoundView.as_view(),
        name='draw-public-for-round'),
    path('sides/',
        views.PublicSideAllocationsView.as_view(),
        name='draw-public-side-allocations'),
]
