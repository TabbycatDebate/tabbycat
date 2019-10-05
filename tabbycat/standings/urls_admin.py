from django.urls import include, path

from . import views

urlpatterns = [
    path('round/<int:round_seq>/', include([
        path('',
            views.StandingsIndexView.as_view(),
            name='standings-index'),
        path('team/',
            views.TeamStandingsView.as_view(),
            name='standings-team'),
        path('team/<slug:category>/',
            views.BreakCategoryStandingsView.as_view(),
            name='standings-break-category'),

        path('email/',
            views.EmailTeamStandingsView.as_view(),
            name='progress-email'),

        path('speaker/',
            views.SpeakerStandingsView.as_view(),
            name='standings-speaker'),
        path('speaker/<slug:category>/',
            views.SpeakerCategoryStandingsView.as_view(),
            name='standings-speaker-category'),
        path('reply/',
            views.ReplyStandingsView.as_view(),
            name='standings-reply'),

        path('diversity/',
            views.DiversityStandingsView.as_view(),
            name='standings-diversity'),
    ])),
]
