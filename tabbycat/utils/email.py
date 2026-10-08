from email.utils import formataddr
from typing import Optional

from django.conf import settings


def tenant_email_address(schema_name: str) -> Optional[str]:
    email_domain = getattr(settings, 'EMAIL_DOMAIN', '')
    if email_domain:
        return '%s@%s' % (schema_name, email_domain)
    return None


def tenant_from_email(tenant, display_name: Optional[str] = None) -> str:
    address = tenant_email_address(tenant.schema_name)
    if address:
        return formataddr((display_name or tenant.name, address))
    return settings.DEFAULT_FROM_EMAIL
