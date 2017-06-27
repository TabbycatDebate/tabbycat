from django import template

register = template.Library()


@register.filter
def metricformat(value):
    if isinstance(value, float):
        value = "{0:.2f}".format(value).split('.')
        return value[0] + '<small class="text-muted">' + '.' + value[1] + '</small>'
    else:
        return str(value)


@register.filter
def rankingformat(value):
    # Of the format (1, False); where true/false connotes a shared rank
    if value[0] is None:
        return ""
    string = str(value[0])
    if value[1]:
        string += "="
    return string
