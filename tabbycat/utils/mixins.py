import logging
import os
from typing import Optional, TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import connection
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import ContextMixin

from users.permissions import has_permission

if TYPE_CHECKING:
    from users.permissions import permission_type

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


# ==============================================================================
# Mixins regulating access based on user account status
# ==============================================================================

class AdministratorMixin(UserPassesTestMixin, ContextMixin):
    """Mixin for views that are for administrators."""
    view_role = "admin"
    for_admin = True
    view_permission: Optional['permission_type'] = None
    edit_permission: Optional['permission_type'] = None

    def get_context_data(self, **kwargs):
        kwargs["user_role"] = self.view_role
        kwargs['can_edit'] = has_permission(self.request.user, self.get_edit_permission(), self.tournament) if hasattr(self, 'tournament') else None
        return super().get_context_data(**kwargs)

    def get_view_permission(self) -> Optional['permission_type']:
        return self.view_permission or self.edit_permission

    def get_edit_permission(self) -> Optional['permission_type']:
        return self.edit_permission

    def test_func(self) -> bool:
        if not hasattr(self, 'tournament'):
            return self.request.user.is_superuser

        view_perm = False
        if self.request.method == 'GET' and self.get_view_permission() is not None:
            view_perm = has_permission(self.request.user, self.get_view_permission(), self.tournament)
            if view_perm:
                return True
        if (not view_perm or self.request.method in ['POST', 'PUT']) and self.get_edit_permission() is not None:
            return has_permission(self.request.user, self.get_edit_permission(), self.tournament)
        return self.request.user.is_superuser


class AssistantMixin(LoginRequiredMixin, ContextMixin):
    """Mixin for views that are for assistants."""
    view_role = "assistant"

    def get_context_data(self, **kwargs):
        kwargs["user_role"] = self.view_role
        return super().get_context_data(**kwargs)


class AccessWebsocketMixin:
    """Checks the user's permissions before allowing a connection.
    Classes using this mixin must inherit from WebsocketConsumer."""

    def connect(self):
        if self.access_permitted():
            return super().connect()
        else:
            return self.close()


class LoginRequiredWebsocketMixin(AccessWebsocketMixin):

    def access_permitted(self):
        return self.scope["user"].is_authenticated


class SuperuserRequiredWebsocketMixin(AccessWebsocketMixin):

    access_permission = False

    def access_permitted(self):
        return has_permission(self.scope["user"], self.access_permission, self.tournament)


# ==============================================================================
# Miscellaneous mixins
# ==============================================================================

class WarnAboutDatabaseUseMixin(ContextMixin):
    """Mixin for views that should stop people exceeding database counts.

    If a user has hit 8000 rows they have received Heroku's shut down
    notification. They are probably fine to finish current tournament even if it
    exceeds these limits because of the one-week grace period. However, they
    should not create new tournaments as this typically happens after the grace
    period and is thus subject to major disruptions."""

    def get_database_row_count(self):
        cursor = connection.cursor()
        cursor.execute("SELECT SUM(n_live_tup) FROM pg_stat_user_tables;")
        return cursor.fetchone()[0]

    def get_context_data(self, **kwargs):
        if 'DATABASE_URL' in os.environ and self.request.user.is_authenticated:
            rows = self.get_database_row_count()
            if rows >= 8000:
                kwargs['database_rows_used'] = rows

        return super().get_context_data(**kwargs)


class WarnAboutLegacySendgridConfigVarsMixin(ContextMixin):
    """Mixin for views that should warn about legacy SendGrid settings that were
    removed in version 2.6.0 (Ocicat).

    When removing, also remove the relevant block in settings/heroku.py, and
    templates/errors/legacy_sendgrid_warning.html (and references thereto).
    """

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated and getattr(settings, 'USING_LEGACY_SENDGRID_CONFIG_VARS', False):
            kwargs['using_legacy_sendgrid_config_vars'] = True
        return super().get_context_data(**kwargs)


class CacheMixin:
    """Mixin for views that cache the page and need to update quickly."""

    cache_timeout = settings.PUBLIC_FAST_CACHE_TIMEOUT

    @method_decorator(cache_page(cache_timeout))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
