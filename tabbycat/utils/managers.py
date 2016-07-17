from django.core.exceptions import ObjectDoesNotExist


class LookupByNameFieldsMixin:
    """Adds the ability to look up by searching a number of name fields for an
    exact match. For example, a model might have short names, long names and
    abbreviations; this mixin would allow lookups that will match any of the
    three.

    This mixin should be added to managers (not models)."""

    name_fields = []

    def lookup(self, name, **kwargs):
        for field in self.name_fields:
            try:
                kwargs[field] = name
                return self.get(**kwargs)
            except ObjectDoesNotExist:
                kwargs.pop(field)
        raise self.model.DoesNotExist("No %s matching '%s'" % (self.model._meta.verbose_name, name))
