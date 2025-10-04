import json
from base64 import b64encode
from decimal import Decimal, ROUND_DOWN
from typing import Optional

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

from .models import LineItem, PriceItem


def add_item(items: list[PriceItem], item_type: PriceItem.ItemType, quantity: int) -> Optional[LineItem]:
    if (
        item := next((i for i in items if i.item_type == item_type), None)
    ) and quantity > 0:
        return LineItem(item=item, quantity=quantity)


def get_application_fee(amount, currency):
    # settings.PAYMENT_FEE_PERCENTAGE
    return Decimal(amount * Decimal('0.025') + Decimal(settings.PAYMENT_FEE_FIXED[currency])).quantize(Decimal(1) / Decimal(currency.minor_unit), rounding=ROUND_DOWN)


def generate_paypal_access_token():
    basic = HTTPBasicAuth(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)
    req = requests.post('https://api-m.sandbox.paypal.com/v1/oauth2/token', auth=basic, data={'grant_type': 'client_credentials'})
    return req.json()['access_token']


def generate_auth_assertion(merchant_id):
    def b64_dict(d):
        return b64encode(json.dumps(d).encode('utf-8'))
    return b64_dict({"alg": "none"}) + b'.' + b64_dict({"iss": settings.PAYPAL_CLIENT_ID, "payer_id": merchant_id}) + b'.'


def generate_paypal_order(connection, amount, line_items, payment):
    merchant_id = connection.external_id
    req = requests.post('https://api-m.sandbox.paypal.com/v2/checkout/orders', headers={
        'Authorization': f'Bearer {generate_paypal_access_token()}',
        'PayPal-Partner-Attribution-Id': settings.PAYPAL_BUILD_NOTATION_CODE,
        'PayPal-Auth-Assertion': generate_auth_assertion(merchant_id),
    }, json={
        'intent': 'CAPTURE',
        'purchase_units': [{
            'custom_id': str(payment.id),
            'invoice_id': str(payment.invoices[0].id) if len(payment.invoices) == 1 else None,
            'items': [
                {'name': li.item.name, 'quantity': li.quantity, 'unit_amount': {'currency_code': payment.currency, 'value': li.item.amount}}
                for li in line_items
            ],
            'amount': {
                'currency_code': payment.currency,
                'value': str(payment.amount),
            },
            'payment_instruction': {
                'platform_fees': [{'amount': {'currency': payment.currency, 'value': str(get_application_fee(payment.amount, payment.currency))}}],
            },
        }],
    })
    return req.json()


def complete_paypal_order(connection, order_id):
    merchant_id = connection.external_id
    req = requests.post(f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture', headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {generate_paypal_access_token()}',
        'PayPal-Auth-Assertion': generate_auth_assertion(merchant_id),
    })
    return req.json()
