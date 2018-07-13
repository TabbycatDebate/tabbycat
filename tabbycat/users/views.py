from .forms import TabRegistrationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.core.exceptions import PermissionDenied

from dynamic_preferences.registries import global_preferences_registry


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
        elif form.instance.key == assist_key:
            form.instance.type = ASSISTANT
        else:
            raise PermissionDenied
        return super().form_valid(form)