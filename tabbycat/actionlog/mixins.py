from django.contrib.auth import get_user_model

from utils.misc import get_ip_address

from .models import ActionLogEntry

User = get_user_model()


class LogActionMixin:
    """Mixin for views that log an action in the action log when a form is
    successfully submitted.

    Views using this mixin should specify an `action_log_type` (or override
    `get_action_log_type()`), and provide an implementation for
    `get_action_log_fields()` that calls its `super()`. The mixin will add an
    `ActionLogEntry` instance when the form is successfully submitted.

    This mixin is best used with views that also derive from `FormMixin`
    somehow. For forms that don't, they can call `self.log_action()` explicitly.
    """

    action_log_type = None

    def get_action_log_type(self):
        """Returns the value that should go in the type field of the
        ActionLogEntry instance. The default implementation returns
        self.action_log_type. Subclasses may override this method.
        """
        return self.action_log_type

    def get_action_log_fields(self, **kwargs):
        """Returns a dict that should be passed as keyword arguments to the
        `ActionLogEntry` instance. Subclasses should implement this method by
        adding to the dictionary `kwargs` and calling the `super()` method. For
        example:
        ```
            kwargs['fieldname'] = self.object
            return super().get_action_log_fields(**kwargs)
        ```

        The default implementation checks if there is a valid user and
        tournament, and if so, adds those keyword arguments if they're not
        already there. Subclasses therefore need not worry about the
        `tournament` and `user` fields of `ActionLogEntry` if they're calling
        the `super()` method.
        """
        if hasattr(self, 'get_tournament'):
            kwargs.setdefault('tournament', self.get_tournament())
        required_fields = ActionLogEntry.REQUIRED_FIELDS_BY_ACTION_TYPE[self.get_action_log_type()]
        if hasattr(self, 'get_round') and 'round' in required_fields:
            kwargs.setdefault('round', self.get_round())
        if hasattr(self.request, 'user') and isinstance(self.request.user, User):
            kwargs.setdefault('user', self.request.user)
        return kwargs

    def log_action(self, **kwargs):
        ip_address = get_ip_address(self.request)
        action_log_fields = self.get_action_log_fields()
        action_log_fields.update(kwargs)
        ActionLogEntry.objects.log(type=self.get_action_log_type(),
                                   ip_address=ip_address,
                                   **action_log_fields)

    def form_valid(self, form):
        self.log_action()
        return super().form_valid(form)
