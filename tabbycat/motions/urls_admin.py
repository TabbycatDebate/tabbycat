from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^edit/$',
        views.EditMotionsView.as_view(),
        name='motions-edit'),
    url(r'^assign/$',
        views.motions_assign,
        name='motions_assign'),
    url(r'^release/$',
        views.ReleaseMotionsView.as_view(),
        name='motions-release'),
    url(r'^unrelease/$',
        views.UnreleaseMotionsView.as_view(),
        name='motions-unrelease'),
    url(r'^display/$',
        views.DisplayMotionsView.as_view(),
        name='motions-display'),
]
