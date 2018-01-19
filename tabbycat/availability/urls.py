from django.urls import include, path

from . import views

urlpatterns = [
    path('round/<int:round_seq>/', include([
        # Overview
        path('',
            views.AvailabilityIndexView.as_view(),
            name='availability-index'),

        # Bulk Updates
        path('all/update/', views.CheckInAllInRoundView.as_view(),
            name='availability-checkin-all'),
        path('previous/update/', views.CheckInAllFromPreviousRoundView.as_view(),
            name='availability-checkin-previous'),

        # Adjudicators
        path('adjudicators/', views.AvailabilityTypeAdjudicatorView.as_view(),
            name='availability-adjudicators'),
        path('adjudicators/update/', views.UpdateAdjudicatorsAvailabilityView.as_view(),
            name='availability-update-adjudicators'),
        path('adjudicators/update/breaking/', views.CheckInAllBreakingAdjudicatorsView.as_view(),
            name='availability-checkin-breaking-adjudicators'),

        # Teams
        path('teams/', views.AvailabilityTypeTeamView.as_view(),
            name='availability-teams'),
        path('teams/update/', views.UpdateTeamsAvailabilityView.as_view(),
            name='availability-update-teams'),

        # Venues
        path('venues/', views.AvailabilityTypeVenueView.as_view(),
            name='availability-venues'),
        path('venues/update/', views.UpdateVenuesAvailabilityView.as_view(),
            name='availability-update-venues'),
    ])),
]
