from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from tournaments.models import Round, Tournament
from users.models import Group, Membership
from utils.misc import reverse_tournament

User = get_user_model()


class InvitationTestMixin:

    def setUp(self):
        super().setUp()
        self.tournament = Tournament.objects.create(slug="invitations", name="Invitations")
        Round.objects.create(tournament=self.tournament, seq=1)


class TestInviteUser(InvitationTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.role = Group.objects.create(tournament=self.tournament, name="Tab staff")
        self.client.force_login(User.objects.create_superuser("admin", "admin@example.com", "password"))

    def invite(self, *emails):
        return self.client.post(reverse_tournament('invite-user', self.tournament), {
            'emails': "\n".join(emails),
            'role': self.role.pk,
        })

    def assertInvited(self, email, username):  # noqa: N802
        user = User.objects.get(email=email)
        self.assertEqual(user.username, username)
        self.assertTrue(Membership.objects.filter(user=user, group=self.role).exists())
        self.assertTrue(any(message.to == [email] for message in mail.outbox))

    def test_invite_uses_local_part_as_username(self):
        self.assertEqual(self.invite("alice@example.com").status_code, 302)
        self.assertInvited("alice@example.com", "alice")

    def test_invite_with_existing_username(self):
        User.objects.create_user("alice", "other@example.com", "password")
        self.assertEqual(self.invite("alice@example.com").status_code, 302)
        self.assertInvited("alice@example.com", "alice2")
        self.assertEqual(User.objects.get(username="alice").email, "other@example.com")

    def test_invite_with_existing_username_of_different_case(self):
        User.objects.create_user("Alice", "other@example.com", "password")
        self.assertEqual(self.invite("alice@example.com").status_code, 302)
        self.assertInvited("alice@example.com", "alice2")

    def test_invite_with_same_local_part_in_one_request(self):
        emails = ("alice@example.com", "alice@example.org", "alice@example.net")
        self.assertEqual(self.invite(*emails).status_code, 302)
        for email, username in zip(emails, ("alice", "alice2", "alice3")):
            self.assertInvited(email, username)

    def test_reinvite_keeps_existing_username(self):
        self.invite("alice@example.com")
        self.assertEqual(self.invite("alice@example.com").status_code, 302)
        self.assertEqual(User.objects.filter(email="alice@example.com").count(), 1)
        self.assertInvited("alice@example.com", "alice")


class TestAcceptInvitation(InvitationTestMixin, TestCase):

    password = "correct-horse-battery-staple"

    def setUp(self):
        super().setUp()
        self.invitee = User.objects.create(username="alice", email="alice@example.com")

    def accept(self, username):
        url = reverse_tournament('accept-invitation', self.tournament, kwargs={
            'uidb64': urlsafe_base64_encode(force_bytes(self.invitee.pk)),
            'token': default_token_generator.make_token(self.invitee),
        })
        # The view moves the token into the session and redirects before showing the form
        form_url = self.client.get(url).url
        return self.client.post(form_url, {
            'username': username,
            'new_password1': self.password,
            'new_password2': self.password,
        })

    def assertRejected(self, response):  # noqa: N802
        self.assertContains(response, "A user with that username already exists.")
        self.invitee.refresh_from_db()
        self.assertEqual(self.invitee.username, "alice")
        self.assertFalse(self.invitee.check_password(self.password))

    def test_accept_with_new_username(self):
        self.assertEqual(self.accept("chosen").status_code, 302)
        self.invitee.refresh_from_db()
        self.assertEqual(self.invitee.username, "chosen")
        self.assertTrue(self.invitee.check_password(self.password))

    def test_accept_keeping_placeholder_username(self):
        self.assertEqual(self.accept("alice").status_code, 302)
        self.invitee.refresh_from_db()
        self.assertTrue(self.invitee.check_password(self.password))

    def test_accept_with_taken_username(self):
        User.objects.create_user("taken", "taken@example.com", "password")
        self.assertRejected(self.accept("taken"))

    def test_accept_with_taken_username_of_different_case(self):
        User.objects.create_user("taken", "taken@example.com", "password")
        self.assertRejected(self.accept("TAKEN"))
