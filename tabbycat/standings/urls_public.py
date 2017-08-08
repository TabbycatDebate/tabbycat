from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^current_standings/$',
        views.PublicCurrentTeamStandingsView.as_view(),
        name='standings-public-teams-current'),
    url(r'^team/$',
        views.PublicTeamTabView.as_view(),
        name='standings-public-tab-team'),
    url(r'^speaker/$',
        views.PublicSpeakerTabView.as_view(),
        name='standings-public-tab-speaker'),
    url(r'^speaker/(?P<category>\w+)/$',
        views.PublicSpeakerCategoryTabView.as_view(),
        name='standings-public-tab-speaker-category'),

    url(r'^replies/$',
        views.PublicReplyTabView.as_view(),
        name='standings-public-tab-replies'),
    url(r'^motions/$',
        views.PublicMotionsTabView.as_view(),
        name='standings-public-tab-motions'),
    url(r'^diversity/$',
        views.PublicDiversityStandingsView.as_view(),
        name='standings-public-diversity'),
]
