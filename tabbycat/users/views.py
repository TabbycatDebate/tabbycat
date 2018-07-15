from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from dynamic_preferences.registries import global_preferences_registry

from .forms import TabRegistrationForm


class SignUp(CreateView):
    ADMIN, ASSISTANT = "admin", "assistant"
    form_class = TabRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
    exclude = []

    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)
        form.instance.key = self.kwargs['key']
        if not form.instance.key:
            raise PermissionDenied
        return form

    def form_valid(self, form):
        prefs = global_preferences_registry.manager()
        enable_admin_key = prefs['accounts__enable_admin_account_key']
        admin_key = prefs['accounts__admin_account_key']
        enable_assist_key = prefs['accounts__enable_assistant_account_key']
        assist_key = prefs['accounts__assistant_account_key']
        if form.instance.key == admin_key and enable_admin_key:
            form.instance.type = self.ADMIN
            form.instance.is_superuser = True
            messages.success(
                self.request,
                _("You have successfully created a new administrator account. You can now log in.")
            )
        elif form.instance.key == assist_key and enable_assist_key:
            form.instance.type = self.ASSISTANT
            messages.success(
                self.request,
                _("You have successfully created a new assistant account. You can now log in.")
            )
        else:
            raise PermissionDenied
        return super().form_valid(form)
