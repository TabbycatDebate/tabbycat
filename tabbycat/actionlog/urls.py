from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^json/latest/$',
        views.LatestActionsView.as_view(),
        name='actionlog-latest-json'),
]
