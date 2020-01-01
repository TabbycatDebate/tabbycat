from django.urls import include, path

from . import views

urlpatterns = [
    path('round/<int:round_seq>/', include([
        path('edit/',
            views.EditMotionsView.as_view(),
            name='motions-edit'),
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

    path('statistics/',
        views.MotionStatisticsView.as_view(),
        name='motions-statistics'),
]
