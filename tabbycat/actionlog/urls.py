from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^latest_actions/$',
        views.LatestActionsView.as_view(),
        name='actionlog-latest-json'),
]
