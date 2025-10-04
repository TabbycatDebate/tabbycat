from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class Currency(TextChoices):
    cad = 'cad', _("Canadian Dollar")
    eur = 'eur', _("Euro")
    gbp = 'gbp', _("British Pound")
    usd = 'usd', _("United States Dollar")

    @property
    def minor_unit(self):
        units = {
            100: (Currency.cad, Currency.eur, Currency.gbp, Currency.usd),
        }
        for val, currencies in units.items():
            if self in currencies:
                return val
        else:
            return ValueError
