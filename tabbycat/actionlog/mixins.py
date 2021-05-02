from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model

from actionlog.consumers import ActionLogEntryConsumer
from tournaments.models import Round, Tournament
from utils.misc import get_ip_address

from .models import ActionLogEntry

User = get_user_model()


class LogActionMixin:
    """Mixin for views that log an action in the action log when a form is
    successfully submitted.

    Views using this mixin should specify an `action_log_type` and, if
    applicable, an `action_log_content_object_attr`. The mixin will add an
    `ActionLogEntry` instance when the form is successfully submitted.

    This mixin is best used with views that also derive from `FormMixin`
    somehow. For forms that don't, they can call `self.log_action()` explicitly.
    """

    action_log_type = None
    action_log_content_object_attr = None

    def get_action_log_type(self):
        """Returns the value that should go in the type field of the
        ActionLogEntry instance. The default implementation returns
        self.action_log_type. Subclasses may override this method.
        """
        return self.action_log_type

    def get_action_log_content_object(self):
        """Returns the content object that should be stored in this action.
        The default implementation looks in `self.action_log_content_object_attr`,
        and if present, it grabs `getattr(self, self.action_log_content_object_attr)`.
        For example, if the `action_log_content_object_attr` class attribute is
        set to "adj_feedback", it grabs `self.adj_feedback`.

        If `action_log_content_object_attr` is not provided, and there is a
        `round` or `tournament` property, it returns the result of
        one of these calls, in that order. Therefore, subclasses need not set
        `action_log_content_object_attr` if the correct content object is a
        Round or Tournament.

        If none of those three are available, it returns None.

        Subclasses can override this method to return the content object
        to be stored with the action log entry.
        """
        if self.action_log_content_object_attr is not None:
            return getattr(self, self.action_log_content_object_attr)
        elif hasattr(self, 'round') and isinstance(self.round, Round):
            return self.round
        elif hasattr(self, 'tournament') and isinstance(self.tournament, Tournament):
            return self.tournament
        else:
            return None

    def get_action_log_fields(self, **kwargs):
        """Returns a dict that should be passed as keyword arguments to the
        `ActionLogEntry` instance.

        The default implementation adds the following:
            - the `type` field, from `get_action_log_type()`
            - the `content_object` field, from `get_action_log_content_object()`
            - the `tournament` field if there is a valid `tournament` property
            - the `round` field if there is a valid `round` property
            - the `user` field if there is a valid user

        If overriding this method, subclasses should call the super() method.

        Note that the `ip_address` field is filled in `log_action()` calls.
        """
        kwargs.setdefault('type', self.get_action_log_type())
        kwargs.setdefault('content_object', self.get_action_log_content_object())

        if hasattr(self, 'round') and isinstance(self.round, Round):
            kwargs.setdefault('round', self.round)

        if hasattr(self, 'tournament') and isinstance(self.tournament, Tournament):
            kwargs.setdefault('tournament', self.tournament)

        if hasattr(self.request, 'user') and isinstance(self.request.user, User):
            kwargs.setdefault('user', self.request.user)

        return kwargs

    def log_action(self, **kwargs):
        """Logs the action. Subclasses can call this if the class doesn't
        have `FormMixin`. If keyword arguments are provided, they override the
        keyword arguments provided by `get_action_log_fields()`, except for
        `ip_address`, which cannot be overridden.
        """
        ip_address = get_ip_address(self.request)
        action_log_fields = self.get_action_log_fields()
        action_log_fields.update(kwargs)
        log = ActionLogEntry.objects.log(ip_address=ip_address, **action_log_fields)

        # Notify the actionlog consumer to broadcast the event
        if self.tournament:
            print('Broadcasting notification of ActionLogEntryConsumer')
            group_name = ActionLogEntryConsumer.group_prefix + "_" + self.tournament.slug
            async_to_sync(get_channel_layer().group_send)(group_name, {
                "type": "send_json",
                "data": log.serialize,
            })

    # If these methods exist, add `self.log_action()` to them.
    # (If they don't, this should be harmless.)

    def form_valid(self, form):
        self.log_action()
        return super().form_valid(form)

    def formset_valid(self, formset):
        self.log_action()
        return super().formset_valid(formset)
