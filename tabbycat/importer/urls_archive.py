from django.urls import path

from . import views

urlpatterns = [

    path('import/',
        views.TournamentImportArchiveView.as_view(),
        name='importer-archive'),

]
