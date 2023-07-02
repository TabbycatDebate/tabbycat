from django.urls import path

from . import views


urlpatterns = [
    path('invite/', views.InviteUserView.as_view(), name='invite-user'),
]
