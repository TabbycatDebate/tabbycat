from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^edit/$',
        views.EditMotionsView.as_view(),
        name='motions_edit'),
    url(r'^assign/$',
        views.motions_assign,
        name='motions_assign'),
    url(r'^release/$',
        views.ReleaseMotionsView.as_view(),
        name='release_motions'),
    url(r'^unrelease/$',
        views.UnreleaseMotionsView.as_view(),
        name='unrelease_motions'),
    url(r'^display/$',
        views.DisplayMotionsView.as_view(),
        name='draw_display_motions'),
]
