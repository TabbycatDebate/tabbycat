from django.urls import path

from . import views

urlpatterns = [
    path('<slug:url_key>/',
        views.PersonIndexView.as_view(),
        name='privateurls-person-index'),
]
