from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^edit/$',
        views.motions_edit,
        name='motions_edit'),
    url(r'^assign/$',
        views.motions_assign,
        name='motions_assign'),
    url(r'^release/$',
        views.release_motions,
        name='release_motions'),
    url(r'^unrelease/$',
        views.unrelease_motions,
        name='unrelease_motions'),
    url(r'^display/$',
        views.DisplayMotionsView.as_view(),
        name='draw_display_motions'),
]
