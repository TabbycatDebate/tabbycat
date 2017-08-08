from django.conf.urls import url

from . import views

urlpatterns = [

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

    url(r'^novices/$',
        views.NoviceStandingsView.as_view(),
        name='standings-novice'),
    url(r'^pros/$',
        views.ProStandingsView.as_view(),
        name='standings-pro'),
    url(r'^esl/$',
        views.ESLStandingsView.as_view(),
        name='standings-esl'),
    url(r'^efl/$',
        views.EFLStandingsView.as_view(),
        name='standings-efl'),
    url(r'^reply/$',
        views.ReplyStandingsView.as_view(),
        name='standings-reply'),

    url(r'^motions/$',
        views.MotionStandingsView.as_view(),
        name='standings-motion'),
    url(r'^diversity/$',
        views.DiversityStandingsView.as_view(),
        name='standings-diversity'),

]
