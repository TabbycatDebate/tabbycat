from django import template
from django.forms import CheckboxInput, CheckboxSelectMultiple, RadioSelect, Select

register = template.Library()


@register.filter(name='addcss')
def addcss(field, css):
    # BS5: selects need form-select, not form-control
    if css == "form-control" and isinstance(field.field.widget, Select):
        css = "form-select"
    return field.as_widget(attrs={"class": css})


@register.filter(name='is_choice_widget')
def is_choice_widget(field):
    widget = field.field.widget
    return isinstance(widget, (RadioSelect, CheckboxSelectMultiple))


@register.filter(name='is_checkbox')
def is_checkbox(field):
    return isinstance(field.field.widget, CheckboxInput)


@register.filter(name='addboundwidgetcss')
def addboundwidgetcss(widget, css):
    widget.data.setdefault('attrs', {}).setdefault('class', '')
    widget.data['attrs']['class'] += " " + css
    return widget
