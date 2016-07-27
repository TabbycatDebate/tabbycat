from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.PublicMotionsView.as_view(), name='motions-public'),
]
