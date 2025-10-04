from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from . import views


urlpatterns = [
    path('webhooks/', include([
        path('paypal/', csrf_exempt(views.PayPalWebhookView.as_view()), name='paypal-webhook'),
        path('stripe/', csrf_exempt(views.StripeWebhookView.as_view()), name='stripe-webhook'),
    ])),
]
