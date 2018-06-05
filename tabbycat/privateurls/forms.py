from django import forms

from django.utils.translation import gettext as _


class EmailBodyField(forms.CharField):

    label = _("Message")
    required = True
    widget = forms.Textarea
    help_text = _(
        "Use '%name' and '%url' as placeholders for the judge's name and their private URL"
        ", respectively in the message body.")

    def validate(self, value):
        super(EmailBodyField, self).validate(value)

        # Check if includes URL variable
        if '%url' not in value:
            raise forms.ValidationError(_("'%url' must be present in the email body"))


class MassBallotEmailForm(forms.Form):
    subject_line = forms.CharField(label=_("Subject"), required=True, max_length=78)
    message_body = EmailBodyField()


class MassFeedbackEmailForm(forms.Form):
    team_subject = forms.CharField(label=_("Subject for team emails"), required=True, max_length=78)
    team_message = EmailBodyField()
    judge_subject = forms.CharField(label=_("Subject for judge emails"), required=True, max_length=78)
    judge_message = EmailBodyField()
