from django.urls import include, path

from . import views


urlpatterns = [

    path('<slug:tournament_slug>/', include([
        path('<int:round_seq>/', include([
        ])),

    ])),

]
