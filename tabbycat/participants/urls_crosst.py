from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^shifts/(?P<url_key>\w+)/$',
        views.PublicConfirmShiftView.as_view(),
        name='participants-public-confirm-shift')
]