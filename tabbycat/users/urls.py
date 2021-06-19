from django.urls import include, path

from . import views


urlpatterns = [
    path('',
        include('django.contrib.auth.urls')),
    path('signup/<slug:key>/', views.SignUpView.as_view(), name='signup'),
]
