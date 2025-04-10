from django.urls import include, path

from participants.models import Adjudicator, Institution, Speaker, Team

from . import views


urlpatterns = [
    path('institutions/', include([
        path('', views.InstitutionRegistrationTableView.as_view(), name='reg-institution-list'),
        path('questions/', views.CustomQuestionFormsetView.as_view(question_model=Institution), name='reg-institution-questions'),
    ])),
    path('teams/', include([
        path('', views.TeamRegistrationTableView.as_view(), name='reg-team-list'),
        path('questions/', views.CustomQuestionFormsetView.as_view(question_model=Team), name='reg-institution-questions'),
    ])),
    path('adjudicators/', include([
        path('', views.AdjudicatorRegistrationTableView.as_view(), name='reg-adjudicator-list'),
        path('questions/', views.CustomQuestionFormsetView.as_view(question_model=Adjudicator), name='reg-institution-questions'),
    ])),
    path('speakers/questions/', views.CustomQuestionFormsetView.as_view(question_model=Speaker), name='reg-institution-questions'),
]
