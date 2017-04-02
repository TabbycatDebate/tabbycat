from django.conf.urls import url

from . import views

urlpatterns = [

    # Divisions Specific
    url(r'^divisions/$',
        views.PublicDivisionsView.as_view(),
        name='public_divisions'),
    url(r'^admin/divisions/allocate/$',
        views.DivisionsAllocatorView.as_view(),
        name='division_allocations'),

    # POST METHODS
    url(r'^admin/divisions/set_venue_category/$',
        views.SetDivisionVenueCategoryView.as_view(),
        name='set_division_venue_category'),
    url(r'^admin/divisions/set_team_division/$',
        views.SetTeamDivisionView.as_view(),
        name='set_team_division'),
    url(r'^admin/divisions/set_division_time/$',
        views.SetDivisionTimeView.as_view(),
        name='set_division_time'),

    # MANUAL ACTIONS
    url(r'^admin/divisions/create/$',
        views.CreateDivisionView.as_view(),
        name='create_division'),
    url(r'^admin/divisions/create_division_allocation/$',
        views.CreateDivisionAllocationView.as_view(),
        name='create_division_allocation'),
    url(r'^admin/divisions/create_byes/$',
        views.CreateByesView.as_view(),
        name='create_byes')

]
