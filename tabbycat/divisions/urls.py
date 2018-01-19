from django.urls import path

from . import views

urlpatterns = [

    # Divisions Specific
    path('divisions/',
        views.PublicDivisionsView.as_view(),
        name='public_divisions'),
    path('admin/divisions/allocate/',
        views.DivisionsAllocatorView.as_view(),
        name='division_allocations'),

    # POST METHODS
    path('admin/divisions/set_venue_category/',
        views.SetDivisionVenueCategoryView.as_view(),
        name='set_division_venue_category'),
    path('admin/divisions/set_team_division/',
        views.SetTeamDivisionView.as_view(),
        name='set_team_division'),
    path('admin/divisions/set_division_time/',
        views.SetDivisionTimeView.as_view(),
        name='set_division_time'),

    # MANUAL ACTIONS
    path('admin/divisions/create/',
        views.CreateDivisionView.as_view(),
        name='create_division'),
    path('admin/divisions/create_division_allocation/',
        views.CreateDivisionAllocationView.as_view(),
        name='create_division_allocation'),
    path('admin/divisions/create_byes/',
        views.CreateByesView.as_view(),
        name='create_byes')

]
