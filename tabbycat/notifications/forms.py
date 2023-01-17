from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.template import Template, TemplateSyntaxError
from django.utils.translation import gettext as _, gettext_lazy
from django_summernote.widgets import SummernoteWidget


class TestEmailForm(forms.Form):
    """Simple form that just sends a test email."""

    recipient = forms.EmailField(label=gettext_lazy("Recipient email address"), required=True)

    def send_email(self, host: str) -> str:
        send_mail(
            _("Test email from %(host)s") % {'host': host},
            _("Congratulations! If you're reading this message, your email "
              "backend on %(host)s looks all good to go!") % {'host': host},
            settings.DEFAULT_FROM_EMAIL,
            [self.cleaned_data['recipient']],
        )
        return self.cleaned_data['recipient']


class BasicEmailForm(forms.Form):
    """A base class for an email form with fields for subject/message

    Note that the list of recipients is handled by Vue, bypassing this Form."""

    subject_line = forms.CharField(label=_("Subject"), required=True, max_length=78)
    message_body = forms.CharField(label=_("Message"), required=True, widget=SummernoteWidget(
        attrs={'height': 150, 'class': 'form-summernote'}))

    def clean_as_template(self, field_name: str) -> str:
        try:
            Template(self.cleaned_data[field_name])
        except TemplateSyntaxError as e:
            raise forms.ValidationError(e)
        return self.cleaned_data[field_name]

    def clean_subject_line(self) -> str:
        return self.clean_as_template('subject_line')

    def clean_message_body(self) -> str:
        return self.clean_as_template('message_body')
