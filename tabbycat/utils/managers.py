from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q


class LookupByNameFieldsMixin:
    """Adds the ability to look up by searching a number of name fields for an
    exact match. For example, a model might have short names, long names and
    abbreviations; this mixin would allow lookups that will match any of the
    three.

    This mixin should be added to managers (not models)."""

    name_fields = []

    def lookup(self, name, **kwargs):
        if len(self.name_fields) < 1:
            raise ImproperlyConfigured("There must be at least one name field in name_fields "
                "when using LookupByNameFieldsMixin.")

        q = Q(**{self.name_fields[0]: name})
        for field in self.name_fields[1:]:
            q |= Q(**{field: name})

        return self.get(q, **kwargs)
