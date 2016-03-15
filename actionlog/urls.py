from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^update/$',
        views.action_log_update,
        name='action_log_update'),
]
