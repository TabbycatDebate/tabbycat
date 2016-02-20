from .models import ActionLogEntry

class LogActionMixin:
    """Mixin for views that log an action in the action log when a form is
    successfully submitted.

    Views using this mixin should specify an `action_log_type` (or override
    `get_action_log_type()`), and provide an implementation for
    `get_action_log_fields()` that calls its `super()`. The mixin will add an
    `ActionLogEntry` instance when the form is successfully submitted.

    This mixin only makes sense when used with views that also derive from
    `FormMixin` somehow.
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
        if hasattr(self.request, 'user'):
            kwargs.setdefault('user', self.request.user)
        return kwargs

    def form_valid(self, form):
        ip_address = get_ip_address(self.request)
        ActionLogEntry.objects.log(type=self.get_action_log_type(),
                ip_address=ip_address, **self.get_action_log_fields())
        return super().form_valid(form)
