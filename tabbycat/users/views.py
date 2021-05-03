from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from dynamic_preferences.registries import global_preferences_registry

from .forms import TabRegistrationForm


class SignUpView(CreateView):
    form_class = TabRegistrationForm
    success_url = reverse_lazy('tabbycat-index')
    template_name = 'signup.html'

    def dispatch(self, request, *args, **kwargs):
        if self.is_page_enabled():
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def is_page_enabled(self):
        prefs = global_preferences_registry.manager()
        admin_key = prefs['global__admin_account_key']
        assist_key = prefs['global__assistant_account_key']
        if not (admin_key or assist_key):
            return False
        if admin_key == self.kwargs['key']:
            self.admin_account = True
            return True
        if assist_key == self.kwargs['key']:
            self.admin_account = False
            return True
        return False

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_superuser = self.admin_account
        user.save()

        if self.admin_account:
            messages.success(self.request,  _("You have successfully created a new administrator account."))
        else:
            messages.success(self.request, _("You have successfully created a new assistant account."))

        login(self.request, user)
        return HttpResponseRedirect(str(self.success_url))
