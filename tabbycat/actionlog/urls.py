from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^latest_actions/$',
        views.GetLatestActions.as_view(),
        name='latest_actions'),
]
