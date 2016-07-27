from django.conf.urls import url

from . import views

urlpatterns = [

    # Divisions Specific
    url(r'^divisions/$',
        views.public_divisions,
        name='public_divisions'),
    url(r'^admin/divisions/allocate/$',
        views.division_allocations,
        name='division_allocations'),

    # POST METHODS
    url(r'^admin/divisions/set_venue_group/$',
        views.set_division_venue_group,
        name='set_division_venue_group'),
    url(r'^admin/divisions/set_team_division/$',
        views.set_team_division,
        name='set_team_division'),
    url(r'^admin/divisions/set_division_time/$',
        views.set_division_time,
        name='set_division_time'),

    # MANUAL ACTIONS
    url(r'^admin/divisions/create/$',
        views.create_division,
        name='create_division'),
    url(r'^admin/divisions/create_division_allocation/$',
        views.create_division_allocation,
        name='create_division_allocation'),
    url(r'^admin/divisions/create_byes/$',
        views.create_byes,
        name='create_byes')

]
