from django.urls import path

from . import views

urlpatterns = [

    path('round/<int:round_seq>/edit/',
        views.EditVenuesView.as_view(),
        name='venues-edit'),
    path('round/<int:round_seq>/save/',
        views.SaveVenuesView.as_view(),
        name='save-debate-venues'),
    path('round/<int:round_seq>/autoallocate/',
        views.AutoAllocateVenuesView.as_view(),
        name='venues-auto-allocate'),

    path('categories/',
        views.VenueCategoriesView.as_view(),
        name='venues-categories'),
    path('constraints/',
        views.VenueConstraintsView.as_view(),
        name='venues-constraints'),
]
