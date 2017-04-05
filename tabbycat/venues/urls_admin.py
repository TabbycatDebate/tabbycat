from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^round/(?P<round_seq>\d+)/edit/$',
        views.EditVenuesView.as_view(),
        name='venues-edit'),
    url(r'^round/(?P<round_seq>\d+)/save/$',
        views.SaveVenuesView.as_view(),
        name='venues-save'),
    url(r'^round/(?P<round_seq>\d+)/autoallocate/$',
        views.AutoAllocateVenuesView.as_view(),
        name='venues-auto-allocate'),

    url(r'^categories/$',
        views.VenueCategoriesView.as_view(),
        name='venues-categories'),
    url(r'^constraints/$',
        views.VenueConstraintsView.as_view(),
        name='venues-constraints'),
]
