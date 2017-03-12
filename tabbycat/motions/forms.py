from django.forms import ModelForm
from django.forms.widgets import CheckboxSelectMultiple
from django.forms.models import ModelMultipleChoiceField

from divisions.models import Division

from .models import Motion


class MyModelChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "D%s @ %s" % (
            obj.name,
            obj.venue_group.short_name,
        )


class ModelAssignForm(ModelForm):

    # TODO: figure out how to filter divisions to fit in this model form
    # def __init__(self, t, *args, **kwargs):
    #     super(ModelAssignForm, self).__init__(**kwargs)
    #     self.fields['divisions'].queryset = Division.objects.filter(tournament=t)

    class Meta:
        model = Motion
        fields = ('divisions',)

    divisions = MyModelChoiceField(widget=CheckboxSelectMultiple,
        queryset=Division.objects.order_by('name'))
