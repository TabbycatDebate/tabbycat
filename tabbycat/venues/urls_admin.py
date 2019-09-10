from django.urls import include, path

from . import views

urlpatterns = [

    path('round/<int:round_seq>/edit/',
        views.EditDebateVenuesView.as_view(),
        name='edit-debate-venues'),
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
    ])),
]
