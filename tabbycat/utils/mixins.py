import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import ContextMixin

logger = logging.getLogger(__name__)


class TabbycatPageTitlesMixin(ContextMixin):
    """Allows all views to set header information in their subclassess obviating
    the need for page template boilerplate and/or page specific templates"""

    page_title = ''
    page_subtitle = ''
    page_emoji = ''

    def get_page_title(self):
        return self.page_title

    def get_page_emoji(self):
        return self.page_emoji

    def get_page_subtitle(self):
        return self.page_subtitle

    def get_context_data(self, **kwargs):
        if "page_title" not in kwargs:
            kwargs["page_title"] = self.get_page_title()
        if "page_subtitle" not in kwargs:
            kwargs["page_subtitle"] = self.get_page_subtitle()

        if "page_emoji" not in kwargs:
            emoji = self.get_page_emoji()
            if emoji:
                kwargs["page_emoji"] = emoji

        return super().get_context_data(**kwargs)


class AdministratorMixin(UserPassesTestMixin, ContextMixin):
    """Mixin for views that are for administrators.
    Requires use to be a superuser."""

    def get_context_data(self, **kwargs):
        kwargs["user_role"] = "admin"
        return super().get_context_data(**kwargs)

    def test_func(self):
        return self.request.user.is_superuser


class AssistantMixin(LoginRequiredMixin, ContextMixin):
    """Mixin for views that are for assistants."""

    def get_context_data(self, **kwargs):
        kwargs["user_role"] = "assistant"
        return super().get_context_data(**kwargs)


class CacheMixin:
    """Mixin for views that cache the page."""

    cache_timeout = settings.PUBLIC_PAGE_CACHE_TIMEOUT

    @method_decorator(cache_page(cache_timeout))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
