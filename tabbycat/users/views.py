import logging
from threading import Lock

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from dynamic_preferences.registries import global_preferences_registry

from .forms import SuperuserCreationForm, TabRegistrationForm

User = get_user_model()
logger = logging.getLogger(__name__)


class SignUpView(CreateView):
    form_class = TabRegistrationForm
    success_url = reverse_lazy('tabbycat-index')
    template_name = 'signup.html'

    def dispatch(self, request, *args, **kwargs):
        if self.is_page_enabled():
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        kwargs['for_admin'] = self.admin_account
        return super().get_context_data(**kwargs)

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


class BlankSiteStartView(CreateView):
    """This view is presented to the user when there are no tournaments and no
    user accounts. It prompts the user to create a first superuser. It rejects
    all requests, GET or POST, if there exists any user account in the
    system."""

    form_class = SuperuserCreationForm
    template_name = "blank_site_start.html"
    lock = Lock()
    success_url = reverse_lazy('tabbycat-index')

    def get(self, request):
        if User.objects.exists():
            logger.warning("Tried to get the blank-site-start view when a user account already exists.")
            return redirect('tabbycat-index')

        return super().get(request)

    def post(self, request):
        with self.lock:
            if User.objects.exists():
                logger.warning("Tried to post the blank-site-start view when a user account already exists.")
                messages.error(request, _("Whoops! It looks like someone's already created the first user account. Please log in."))
                return redirect('login')

            return super().post(request)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.info(self.request, _("Welcome! You've created an account for %s.") % user.username)

        return super().form_valid(form)
