from django import template

register = template.Library()


@register.filter
def metricformat(value):
    if isinstance(value, float):
        value = "{0:.2f}".format(value).split('.')
        return value[0] + '<small>' + '.' + value[1] + '</small>'
    else:
        return str(value)


@register.filter
def rankingformat(value):
    if value[0] is None:
        return ""
    string = str(value[0])
    if value[1]:
        string += "="
    return string
