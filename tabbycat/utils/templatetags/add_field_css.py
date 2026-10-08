from django import template
from django.forms import CheckboxSelectMultiple, RadioSelect

register = template.Library()


@register.filter(name='addcss')
def addcss(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter(name='is_choice_widget')
def is_choice_widget(field):
    widget = field.field.widget
    return isinstance(widget, (RadioSelect, CheckboxSelectMultiple))


@register.filter(name='addboundwidgetcss')
def addboundwidgetcss(widget, css):
    widget.data.setdefault('attrs', {}).setdefault('class', '')
    widget.data['attrs']['class'] += " " + css
    return widget
