from django.urls import include, path

from . import views

urlpatterns = [
    path('round/<int:round_seq>/', include([
        path('edit/',
            views.EditMotionsView.as_view(),
            name='motions-edit'),
        path('copy/',
            views.CopyMotionsView.as_view(),
            name='motions-copy'),
        path('previous/',
            views.CopyPreviousMotionsView.as_view(),
            name='motions-previous'),
        path('release/',
            views.ReleaseMotionsView.as_view(),
            name='motions-release'),
        path('unrelease/',
            views.UnreleaseMotionsView.as_view(),
            name='motions-unrelease'),
        path('display/',
            views.AdminDisplayMotionsView.as_view(),
            name='motions-display'),

        # Email
        path('email/',
            views.EmailMotionReleaseView.as_view(),
            name='motions-email'),
    ])),

    path('statistics/', include([
        path('',
            views.AdminRoundMotionStatisticsView.as_view(),
            name='motions-statistics'),
        path('global/',
            views.AdminGlobalMotionStatisticsView.as_view(),
            name='motions-global-statistics'),
    ])),
]
