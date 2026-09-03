import json

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm, UsernameField
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from notifications.email_tracking import build_hook_id, send_tracked_emails, tournament_from_email
from notifications.models import BulkNotification, SentMessage

from .models import Membership

User = get_user_model()


class SuperuserCreationForm(UserCreationForm):
    """A form that creates a superuser from the given username and password."""

    class Meta(UserCreationForm.Meta):
        fields = ("username", "email")
        labels = {"email": _("Email address")}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user


def split_email_addresses(data: str) -> list[str]:
    items = data.replace('\t', '\n').replace(',', '\n')
    items = items.split('\n')
    items = [item.strip() for item in items]
    return [item for item in items if item]


class InviteUserForm(forms.Form):
    emails = forms.CharField(
        label=_("Email addresses"),
        help_text=_("Separate multiple addresses with commas or new lines."),
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    def __init__(self, tournament, *args, **kwargs):
        self.tournament = tournament
        super().__init__(*args, **kwargs)
        self.fields['role'] = forms.ModelChoiceField(queryset=tournament.group_set.all())

    def clean_emails(self):
        emails = split_email_addresses(self.cleaned_data['emails'])
        if len(emails) == 0:
            raise forms.ValidationError(_("Enter at least one email address."))

        seen = set()
        for email in emails:
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError(_("%(email)s is not a valid email address.") % {'email': email})
            if email.lower() in seen:
                raise forms.ValidationError(_("Duplicate email address: %(email)s") % {'email': email})
            seen.add(email.lower())

        return emails

    def _get_or_create_user(self, email):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split("@")[0],
            },
        )
        Membership.objects.get_or_create(
            user=user,
            group=self.cleaned_data['role'],
        )
        return user, created

    def save(
        self,
        request,
        subject_template_name,
        email_template_name,
        html_email_template_name=None,
        token_generator=default_token_generator,
        extra_email_context=None,
    ):
        current_site = get_current_site(request)
        from_email, reply_to = tournament_from_email(self.tournament)

        bulk_notification = BulkNotification.objects.create(
            event=BulkNotification.EventType.USER_INVITE,
            tournament=self.tournament,
            subject_template=subject_template_name,
            body_template=email_template_name,
        )

        messages = []
        records = []
        email_field_name = User.get_email_field_name()
        extra_email_context = {**(extra_email_context or {}), 'tournament': self.tournament}

        for email in self.cleaned_data['emails']:
            user, created = self._get_or_create_user(email)
            if created and user.password and user.has_usable_password():
                # Don't send email to user if they already created their account
                continue
            user_email = getattr(user, email_field_name)
            user_pk_bytes = force_bytes(User._meta.pk.value_to_string(user))
            context = {
                "email": user_email,
                "domain": current_site.domain,
                "site_name": current_site.name,
                "uid": urlsafe_base64_encode(user_pk_bytes),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if request.is_secure() else "http",
                **extra_email_context,
            }

            subject = loader.render_to_string(subject_template_name, context)
            subject = "".join(subject.splitlines())
            body = loader.render_to_string(email_template_name, context)

            hook_id = build_hook_id(bulk_notification.id, user.pk)
            message = EmailMultiAlternatives(
                subject, body, from_email, [user_email],
                reply_to=reply_to,
                headers={
                    'X-SMTPAPI': json.dumps({'unique_args': {'hook-id': hook_id}}),
                },
            )
            if html_email_template_name is not None:
                html_email = loader.render_to_string(html_email_template_name, context)
                message.attach_alternative(html_email, "text/html")

            messages.append(message)

            raw_message = message.message()
            records.append(SentMessage(
                email=user_email,
                method=SentMessage.METHOD_TYPE_EMAIL,
                context={'email': user_email, 'user_id': user.pk},
                message_id=raw_message['Message-ID'],
                hook_id=hook_id,
                notification=bulk_notification,
            ))

        send_tracked_emails(messages, records)
        return len(messages)


class AcceptInvitationForm(SetPasswordForm):
    username = UsernameField(label=_("Username"), help_text=get_user_model()._meta.get_field('username').help_text)

    field_order = ('username', 'new_password1', 'new_password2')

    def save(self, commit=True):
        self.user.username = self.cleaned_data['username']
        return super().save(commit=commit)
