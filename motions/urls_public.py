from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.public_motions, name='public_motions'),

]