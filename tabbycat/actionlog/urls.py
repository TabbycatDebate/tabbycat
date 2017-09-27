from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^latest/$',
        views.LatestActionsView.as_view(),
        name='actionlog-latest-json'),
]
