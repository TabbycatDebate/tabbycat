from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$',              views.tournament_options,    name='tournament_options'),

]