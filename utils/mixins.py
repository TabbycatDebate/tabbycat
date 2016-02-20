from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin

from .misc import get_ip_address, redirect_tournament

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


class PublicCacheMixin:
    """Mixin for views that cache the page."""

    cache_timeout = settings.PUBLIC_PAGE_CACHE_TIMEOUT

    @method_decorator(cache_page(cache_timeout))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SingleObjectByRandomisedUrlMixin(SingleObjectMixin):
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
    query_pk_and_slug = True
