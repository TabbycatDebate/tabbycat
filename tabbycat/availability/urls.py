from django.conf.urls import url

from . import views

urlpatterns = [
    # Overview
    url(r'^$',
        views.AvailabilityIndexView.as_view(),
        name='availability-index'),

    # # Bulk Updates
    url(r'all/update/$', views.CheckInAllInRoundView.as_view(),
        name='availability-checkin-all'),
    url(r'previous/update/$', views.CheckInAllFromPreviousRoundView.as_view(),
        name='availability-checkin-previous'),

    # Adjs
    url(r'adjudicators/$', views.AvailabilityTypeAdjudicatorView.as_view(),
        name='availability-adjudicators'),
    url(r'adjudicators/update/$', views.UpdateAdjudicatorsAvailabilityView.as_view(),
        name='availability-update-adjudicators'),
    url(r'adjudicators/update/breaking/$', views.CheckInAllBreakingAdjudicatorsView.as_view(),
        name='availability-checkin-breaking-adjudicators'),

    # Teams
    url(r'teams/$', views.AvailabilityTypeTeamView.as_view(),
        name='availability-teams'),
    url(r'teams/update/$', views.UpdateTeamsAvailabilityView.as_view(),
        name='availability-update-teams'),

    # Venues
    url(r'venues/$', views.AvailabilityTypeVenueView.as_view(),
        name='availability-venues'),
    url(r'venues/update/$', views.UpdateVenuesAvailabilityView.as_view(),
        name='availability-update-venues'),

]
