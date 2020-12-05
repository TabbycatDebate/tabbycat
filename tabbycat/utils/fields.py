from django import forms
from django.contrib.postgres.fields import ArrayField


class ChoiceArrayField(ArrayField):
    """
    Reference: https://gist.github.com/danni/f55c4ce19598b2b345ef
    See also: https://code.djangoproject.com/ticket/27704
    """

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.TypedMultipleChoiceField,
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)

        # Skip our parent's formfield implementation completely as we don't
        # care for it.
        return super(ArrayField, self).formfield(**defaults)
