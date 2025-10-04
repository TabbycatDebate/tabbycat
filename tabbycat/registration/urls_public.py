from django.urls import include, path

from . import views


urlpatterns = [
    path('institution/', include([
        path('new/', views.CreateInstitutionFormView.as_view(),
            name='reg-create-institution'),
        path('<slug:url_key>/', include([
            path('',
                views.InstitutionalLandingPageView.as_view(),
                name='reg-inst-landing'),
            path('adjudicator/',
                views.InstitutionalCreateAdjudicatorFormView.as_view(),
                name='reg-inst-create-adj'),
            path('team/',
                views.InstitutionalCreateTeamFormView.as_view(),
                name='reg-inst-create-team'),
            path('balance/',
                views.InstitutionBalanceSummaryView.as_view(),
                name='reg-inst-invoice-balance'),
            path('invoices/<int:invoice_id>/',
                views.InstitutionInvoiceView.as_view(),
                name='reg-inst-invoice'),
        ])),
    ])),
    path('adjudicator/',
        views.PublicCreateAdjudicatorFormView.as_view(),
        name='reg-create-adjudicator'),
    path('team/', include([
        path('',
            views.PublicCreateTeamFormView.as_view(),
            name='reg-create-team'),
        path('<int:pk>/speaker/',
            views.CreateSpeakerFormView.as_view(),
            name='reg-create-speaker'),
    ])),
    path('payments/', include([
        path('paypal/', include([
            path('capture/', views.PayPalCaptureOrderView.as_view(), name='reg-paypal-capture'),
        ])),
        path('<slug:url_key>/', include([
            path('balance/', views.PrivateUrlBalanceSummaryView.as_view(), name='private-url-payment-balance'),
            path('invoices/<int:invoice_id>/', views.PrivateUrlInvoiceView.as_view(), name='private-url-invoice'),
        ])),
    ])),
]
