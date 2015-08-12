from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$',              views.tournament_config,    name='tournament_config'),

]