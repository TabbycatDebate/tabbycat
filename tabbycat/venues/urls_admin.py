from django.urls import path

from . import views

urlpatterns = [

    path('round/<int:round_seq>/edit/',
        views.EditDebateVenuesView.as_view(),
        name='edit-debate-venues'),
    path('categories/',
        views.VenueCategoriesView.as_view(),
        name='venues-categories'),
    path('constraints/',
        views.VenueConstraintsView.as_view(),
        name='venues-constraints'),
]
