from django.urls import include, path

from . import views

urlpatterns = [

    path('round/<int:round_seq>/', include([
        path('edit/',
            views.EditDebateVenuesView.as_view(),
            name='edit-debate-venues'),
        path('edit-legacy/',
            views.LegacyEditVenuesView.as_view(),
            name='legacy-venues-edit'),
        path('save/',
            views.LegacySaveVenuesView.as_view(),
            name='legacy-save-debate-venues'),
        path('autoallocate/',
            views.LegacyAutoAllocateVenuesView.as_view(),
            name='legacy-venues-auto-allocate'),
    ])),

    path('categories/',
        views.VenueCategoriesView.as_view(),
        name='venues-categories'),

    path('constraints/', include([
        path('team/',
            views.VenueTeamConstraintsView.as_view(),
            name='venues-constraints-team'),
        path('adjudicator/',
            views.VenueAdjudicatorConstraintsView.as_view(),
            name='venues-constraints-adjudicator'),
        path('institution/',
            views.VenueInstitutionConstraintsView.as_view(),
            name='venues-constraints-institution'),
        path('division/',
            views.VenueDivisionConstraintsView.as_view(),
            name='venues-constraints-division'),
    ])),
]
