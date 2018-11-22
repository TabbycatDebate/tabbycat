from django.urls import path

from . import views

urlpatterns = [
    path('',
        views.RandomisedUrlsView.as_view(),
        name='privateurls-list'),

    path('generate/',
        views.GenerateRandomisedUrlsView.as_view(),
        name='privateurls-generate'),

    path('email/',
        views.EmailRandomisedUrlsView.as_view(),
        name='privateurls-email'),
]
