from django.urls import include, path

from participants.models import Adjudicator, Coach, Speaker, Team, TournamentInstitution

from . import views


urlpatterns = [
    path('institutions/', include([
        path('', views.InstitutionRegistrationTableView.as_view(), name='reg-institution-list'),
        path('questions/',
            views.CustomQuestionFormsetView.as_view(question_model=TournamentInstitution, success_url='reg-institution-list'),
            name='reg-institution-questions'),
        path('coaches/questions/',
            views.CustomQuestionFormsetView.as_view(question_model=Coach, success_url='reg-institution-list'),
            name='reg-coach-questions'),
    ])),
    path('teams/', include([
        path('', views.TeamRegistrationTableView.as_view(), name='reg-team-list'),
        path('questions/',
            views.CustomQuestionFormsetView.as_view(question_model=Team, success_url='reg-team-list'),
            name='reg-team-questions'),
    ])),
    path('adjudicators/', include([
        path('', views.AdjudicatorRegistrationTableView.as_view(), name='reg-adjudicator-list'),
        path('questions/',
            views.CustomQuestionFormsetView.as_view(question_model=Adjudicator, success_url='reg-adjudicator-list'),
            name='reg-adjudicator-questions'),
    ])),
    path('speakers/questions/',
        views.CustomQuestionFormsetView.as_view(question_model=Speaker, success_url='reg-team-list'),
        name='reg-speaker-questions'),
    path('payments/', include([
        path('', views.AdminPaymentsIndexView.as_view(), name='reg-payments-admin-list'),
        path('connect/', include([
            path('', views.PaymentConnectionView.as_view(), name='reg-payments-connect'),
            path('stripe/', include([
                path('refresh/', views.StripeAccountRefreshView.as_view(), name='stripe-connect-refresh'),
                path('return/', views.StripeAccountReturnView.as_view(), name='stripe-connect-return'),
            ])),
            path('paypal', include([
                path('return/', views.PayPalConnectReturnView.as_view(), name='paypal-connect-return'),
            ])),
        ])),
        path('products/', views.CreateProductsView.as_view(), name='reg-products-edit'),
        path('discount/', views.CreateDiscountView.as_view(), name='reg-create-discount'),
        path('invoice/', include([
            path('new/', views.CreateInvoiceView.as_view(), name='reg-create-invoice'),
            path('<int:pk>/', views.AdminInvoiceView.as_view(), name='reg-admin-invoice-view'),
        ])),
        path('payment/', include([
            path('new/', views.CreatePaymentView.as_view(), name='reg-create-payment'),
            path('<int:pk>/', views.AdminPaymentView.as_view(), name='reg-admin-payment-view'),
        ])),
        path('balance/', include([
            path('institution/<int:pk>/', views.AdminInstitutionBalanceSummaryView.as_view(), name='reg-admin-institution-balance'),
            path('team/<int:pk>/', views.AdminTeamBalanceSummaryView.as_view(), name='reg-admin-team-balance'),
            path('person/<int:pk>/', views.AdminPersonBalanceSummaryView.as_view(), name='reg-admin-person-balance'),
        ])),
    ])),
]
