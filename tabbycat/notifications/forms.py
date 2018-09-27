from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext as _, gettext_lazy


class TestEmailForm(forms.Form):
    """Simple form that just sends a test email."""

    recipient = forms.EmailField(label=gettext_lazy("Recipient email address"), required=True)

    def send_email(self, host):
        send_mail(
            _("Test email from %(host)s") % {'host': host},
            _("Congratulations! If you're reading this message, your email "
              "backend on %(host)s looks all good to go!") % {'host': host},
            settings.DEFAULT_FROM_EMAIL,
            [self.cleaned_data['recipient']],
        )
        return self.cleaned_data['recipient']
