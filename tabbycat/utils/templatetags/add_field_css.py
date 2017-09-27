from django import template

register = template.Library()


@register.filter(name='addcss')
def addcss(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter(name='addboundwidgetcss')
def addboundwidgetcss(widget, css):
    widget.data.setdefault('attrs', {}).setdefault('class', '')
    widget.data['attrs']['class'] += " " + css
    return widget
