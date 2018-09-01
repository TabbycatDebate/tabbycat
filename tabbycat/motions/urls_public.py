from django.urls import include, path

from . import views

urlpatterns = [
    path('',
        views.PublicMotionsView.as_view(),
        name='motions-public'),

    path('statistics/', include([
        path('',
            views.PublicRoundMotionsStatisticsView.as_view(),
            name='motions-public-statistics'),
        path('global/',
            views.PublicGlobalMotionStatisticsView.as_view(),
            name='motions-global-public-statistics'),
    ])),
]
