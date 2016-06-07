from django import template

register = template.Library()


@register.filter
def metricformat(value):
    if isinstance(value, float):
        return "{0:.2f}".format(value)
    else:
        return str(value)
