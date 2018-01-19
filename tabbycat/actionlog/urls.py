from django.urls import path

from . import views

urlpatterns = [
    path('json/latest/',
        views.LatestActionsView.as_view(),
        name='actionlog-latest-json'),
]
