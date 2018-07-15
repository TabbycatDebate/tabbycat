from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from dynamic_preferences.registries import global_preferences_registry

from .forms import TabRegistrationForm


class SignUp(CreateView):
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
        ADMIN, ASSISTANT = "admin", "assistant"
        prefs = global_preferences_registry.manager()
        admin_key = prefs['accounts__admin_account_key']
        assist_key = prefs['accounts__assistant_account_key']
        if form.instance.key == admin_key:
            form.instance.type = ADMIN
            form.instance.is_superuser = True
            messages.success(self.request, _("You have successfully created a new administrator account. You can now log in."))
        elif form.instance.key == assist_key:
            form.instance.type = ASSISTANT
            messages.success(self.request, _("You have successfully created a new assistant account. You can now log in."))
        else:
            raise PermissionDenied
        return super().form_valid(form)
