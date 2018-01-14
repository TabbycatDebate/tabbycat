from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^round/(?P<round_seq>\d+)/', include([
        url(r'^$',
            views.StandingsIndexView.as_view(),
            name='standings-index'),
        url(r'^team/$',
            views.TeamStandingsView.as_view(),
            name='standings-team'),
        url(r'^division/$',
            views.DivisionStandingsView.as_view(),
            name='standings-division'),

        url(r'^speaker/$',
            views.SpeakerStandingsView.as_view(),
            name='standings-speaker'),
        url(r'^speaker/(?P<category>\w+)/$',
            views.SpeakerCategoryStandingsView.as_view(),
            name='standings-speaker-category'),
        url(r'^reply/$',
            views.ReplyStandingsView.as_view(),
            name='standings-reply'),

        url(r'^motions/$',
            views.MotionStandingsView.as_view(),
            name='standings-motion'),
        url(r'^diversity/$',
            views.DiversityStandingsView.as_view(),
            name='standings-diversity'),
    ])),
]
