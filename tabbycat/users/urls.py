from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views


urlpatterns = [
    path('logout/',
        auth_views.LogoutView.as_view(),
        {'next_page': '/'},  # override to specify next_page
        name='logout'),
    path('',
        include('django.contrib.auth.urls')),
    path('signup/<slug:key>/', views.SignUpView.as_view(), name='signup'),
]
