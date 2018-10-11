from django.urls import path

from . import views

urlpatterns = [

    path('round/<int:round_seq>/edit/',
        views.EditDebateVenuesView.as_view(),
        name='edit-debate-venues'),
    path('round/<int:round_seq>/edit-legacy/',
        views.LegacyEditVenuesView.as_view(),
        name='legacy-venues-edit'),
    path('round/<int:round_seq>/save/',
        views.LegacySaveVenuesView.as_view(),
        name='legacy-save-debate-venues'),
    path('round/<int:round_seq>/autoallocate/',
        views.LegacyAutoAllocateVenuesView.as_view(),
        name='legacy-venues-auto-allocate'),

    path('categories/',
        views.VenueCategoriesView.as_view(),
        name='venues-categories'),
    path('constraints/',
        views.VenueConstraintsView.as_view(),
        name='venues-constraints'),
]
