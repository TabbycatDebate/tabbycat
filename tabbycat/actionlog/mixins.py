from django.contrib.auth import get_user_model

from tournaments.models import Round
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
        `get_round()` or `get_tournament()` method, it returns the result of
        one of these calls, in that order. Therefore, subclasses need not set
        `action_log_content_object_attr` if the correct content object is a
        Round or Tournament.

        If none of those three are available, it returns None.

        Subclasses can override this method to return the content object
        to be stored with the action log entry.
        """
        if self.action_log_content_object_attr is not None:
            return getattr(self, self.action_log_content_object_attr)
        elif hasattr(self, 'get_round') and callable(self.get_round):
            return self.get_round()
        elif hasattr(self, 'get_tournament') and callable(self.get_tournament):
            return self.get_tournament()
        else:
            return None

    def get_action_log_fields(self, **kwargs):
        """Returns a dict that should be passed as keyword arguments to the
        `ActionLogEntry` instance.

        The default implementation adds the following:
            - the `type` field, from `get_action_log_type()`
            - the `content_object` field, from `get_action_log_content_object()`
            - the `tournament` field if there is a `get_tournament()` method
            - the `round` field if there is a `get_round()` method
            - the `user` field if there is a valid user

        If overriding this method, subclasses should call the super() method.

        Note that the `ip_address` field is filled in `log_action()` calls.
        """
        kwargs.setdefault('type', self.get_action_log_type())
        kwargs.setdefault('content_object', self.get_action_log_content_object())

        if hasattr(self, 'round') and isinstance(self.round, Round):
            kwargs.setdefault('round', self.round)
        elif hasattr(self, 'get_round') and callable(self.get_round):
            kwargs.setdefault('round', self.get_round())

        if hasattr(self, 'get_tournament') and callable(self.get_tournament):
            kwargs.setdefault('tournament', self.get_tournament())

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
        ActionLogEntry.objects.log(ip_address=ip_address, **action_log_fields)

    def form_valid(self, form):
        self.log_action()
        return super().form_valid(form)
