import logging
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateResponseMixin, TemplateView, View
from django.views.generic.detail import SingleObjectMixin

from tournaments.mixins import TournamentMixin

logger = logging.getLogger(__name__)


class ExpectPost(View):
    """Ensures a POST was made and provides super call with POST data """

    def dispatch(self, request, *args, **kwargs):
        if request.method != "POST":
            return HttpResponseBadRequest("Expected POST")
        else:
            return super().dispatch(request, *args, **kwargs)


class PostOnlyRedirectView(View):
    """Base class for views that only accept POST requests.

    Current implementation redirects to a specified page (by default the home
    page) if a client tries to use a GET request, and shows and logs an error
    message. We might change this in the future just to return HTTP status code
    405 (HTTP method not allowed).

    Views using this class probably want to override both `post()` and
    `get_redirect_url()`. It is assumed that the same redirect will be desired
    the same whether GET or POST is used; it's just that a GET request won't
    do database edits.

    Note: The `post()` implementation of subclasses should call `super().post()`
    rather than returning the redirect directly, in case we decide to make
    `post()` smarter in the future. If there ever arises a need to distinguish
    between the redirects in the GET and POST cases, new methods should be added
    to this base class for this purpose.
    """

    redirect_url = reverse_lazy('tabbycat-index')
    not_post_message = "Whoops! You're not meant to type that URL into your browser."

    def get_redirect_url(self):
        return self.redirect_url

    def get(self, request, *args, **kwargs):
        logger.error("Tried to access a POST-only view with a GET request")
        messages.error(self.request, self.not_post_message)
        return HttpResponseRedirect(self.get_redirect_url())

    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.get_redirect_url())


class JsonDataResponseView(View):
    """Mixings for views that dump back a json response"""

    def get_data():
        pass

    def get(self, request, *args, **kwargs):
        self.request = request
        return HttpResponse(json.dumps(self.get_data()), content_type="text/json")


class SuperuserRequiredMixin(UserPassesTestMixin):
    """Class-based view mixin. Requires user to be a superuser."""

    def test_func(self):
        return self.request.user.is_superuser


class SuperuserOrTabroomAssistantTemplateResponseMixin(LoginRequiredMixin, TemplateResponseMixin):
    """Mixin for views that choose either a superuser view or an assistant view,
    depending on the privileges of the user who is logged in.

    Views using this mixin must define the `superuser_template_name` and
    `assistant_template_name` class attributes."""

    superuser_template_name = None
    assistant_template_name = None

    def get_template_names(self):
        if self.request.user.is_superuser:
            return [self.superuser_template_name]
        else:
            return [self.assistant_template_name]


class CacheMixin:
    """Mixin for views that cache the page."""

    cache_timeout = settings.PUBLIC_PAGE_CACHE_TIMEOUT

    @method_decorator(cache_page(cache_timeout))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SingleObjectFromTournamentMixin(SingleObjectMixin, TournamentMixin):
    """Mixin for views that relate to a single object that is part of a
    tournament. Like SingleObjectMixin, but restricts searches to the relevant
    tournament."""

    def get_queryset(self):
        return super().get_queryset().filter(tournament=self.get_tournament())


class SingleObjectByRandomisedUrlMixin(SingleObjectFromTournamentMixin):
    """Mixin for views that use URLs referencing objects by a randomised key.
    This is just a `SingleObjectMixin` with some options set.

    Views using this mixin should have both a `url_key` group in their URL's
    regular expression, and a primary key group (by default `pk`, inherited from
    `SingleObjectMixin`, but this can be overridden). They should set the
    `model` field of the class as they would for `SingleObjectMixin`. This model
    should have a slug field called `url_key`.
    """
    slug_field = 'url_key'
    slug_url_kwarg = 'url_key'


class VueTableMixin(TemplateView):
    """Mixing that provides shortcuts for adding data when building arrays that
    will end up as rows within a Vue table. Each cell can be represented
    either as a string value or a dictionary to enable richer inline content
    (emoji, links, etc). Functions below return blocks of content (ie not just
     a team name row, but also institution/category status as needed)."""

    template_name = 'base_vue_table.html'

    def get_context_data(self, **kwargs):
        tables = self.get_tables()
        kwargs["tables_count"] = list(range(len(tables)))
        kwargs["tables_data"] = json.dumps([table.jsondict() for table in tables])
        return super().get_context_data(**kwargs)

    def get_table(self):
        raise NotImplementedError("subclasses must implement get_table()")

    def get_tables(self):
        return [self.get_table()]
