from django.urls import include, path

from . import views

urlpatterns = [
    path('',
        views.CustomEmailCreateView.as_view(),
        name='notifications-email'),

    path('round/<int:round_seq>/', include([
        path('<str:event_type>/',
            views.RoundTemplateEmailCreateView.as_view(),
            name='notifications-round-template-email'),
    ])),
    path('t/<str:event_type>/',
    	views.TournamentTemplateEmailCreateView.as_view(),
    	name='notifications-tournament-template-email'),
]
