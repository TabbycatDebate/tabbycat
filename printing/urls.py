from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^scoresheets/$', views.draw_print_scoresheets, name='draw_print_scoresheets'),
    url(r'^feedback/$', views.draw_print_feedback, name='draw_print_feedback'),
]