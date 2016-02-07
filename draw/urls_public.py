from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',
        views.public_draw,
        name='public_draw'),
    url(r'^round/(?P<round_seq>\d+)/$',
        views.public_draw_by_round,
        name='public_draw_by_round'),
    url(r'^all/$',
        views.public_all_draws,
        name='public_all_draws'),
    url(r'^side_allocations/$',
        views.public_side_allocations,
        name='public_side_allocations'),
]
