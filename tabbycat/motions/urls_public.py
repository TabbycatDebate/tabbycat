from django.urls import path

from . import views

urlpatterns = [
    path('',
        views.PublicMotionsView.as_view(),
        name='motions-public'),
    path('statistics/',
        views.PublicMotionStatisticsView.as_view(),
        name='motions-public-statistics'),
]
