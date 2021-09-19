from django import forms


class OptionalChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(OptionalChoiceField, self).__init__(*args, **kwargs)
        self.choices = [(None, '---------')] + list(self.choices)


class SelectPrepopulated(forms.TextInput):
    template_name = 'select_prepopulated_widget.html'

    def __init__(self, data_list, *args, **kwargs):
        super(SelectPrepopulated, self).__init__(*args, **kwargs)
        self.attrs.update({'data_list': data_list})
