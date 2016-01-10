from django.conf.urls import url
from django.core.urlresolvers import reverse
from utils.views import *

from . import views

urlpatterns = [

    url(r'^$',
      views.tournament_options,
      name='tournament_options'),
    url(r'^test/$',
      admin_required(views.TournamentPreferenceFormView.as_view()),
      name="dynamic_preferences.tournament"),

]