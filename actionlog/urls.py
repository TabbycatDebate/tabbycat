from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^latest_actions/$', views.latest_actions, name='latest_actions'),
]
