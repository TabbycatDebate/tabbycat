from django import forms

from django.utils.translation import gettext as _


class EmailBodyField(forms.CharField):

    label = _("Message")
    required = True
    widget = forms.Textarea

    def validate(self, value):
        # Check if includes URL variable
        if '{{ URL }}' not in value:
            raise forms.ValidationError(_("'{{ URL }}' must be present in the email body"))

        super().validate(value)


class MassBallotEmailForm(forms.Form):
    subject_line = forms.CharField(label=_("Subject"), required=True, max_length=78)
    message_body = EmailBodyField(help_text=_(
        "Use '{{ NAME }}' and '{{ URL }}' as placeholders for the judge's name and their private URL"
        ", respectively in the message body."))


class MassFeedbackEmailForm(forms.Form):
    team_subject = forms.CharField(label=_("Subject for team emails"), required=True, max_length=78)
    team_message = EmailBodyField(help_text=_(
        "Use '{{ NAME }}', '{{ TEAM }}', and '{{ URL }}' as placeholders for the judge's name"
        ", team's name, and their private URL, respectively in the message body."))
    judge_subject = forms.CharField(label=_("Subject for judge emails"), required=True, max_length=78)
    judge_message = EmailBodyField(help_text=_(
        "Use '{{ NAME }}' and '{{ URL }}' as placeholders for the judge's name and their private URL"
        ", respectively in the message body."))
