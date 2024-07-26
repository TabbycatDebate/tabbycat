from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group as AuthGroup
from django.forms import ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _

from .models import Group, Membership, UserPermission


# ==============================================================================
# Authentication and Authorization
# ==============================================================================

admin.site.unregister(AuthGroup) # No need to show groups


class UserPermissionInline(admin.TabularInline):
    model = UserPermission
    fields = ('permission', 'tournament')


class MembershipInline(admin.TabularInline):
    model = Membership
    fields = ('group',)


class CustomUserLabelsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_staff'].help_text = _("Users with staff status can"
            " view and edit the Edit Database area. This is potentially "
            "dangerous and should be reserved for the actual tab director(s).")


class UserChangeFormExtended(CustomUserLabelsMixin, UserChangeForm):
    group_set = ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)


class UserCreationFormExtended(CustomUserLabelsMixin, UserCreationForm):
    group_set = ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'is_superuser')
    inlines = (UserPermissionInline, MembershipInline)

    fieldsets = ( # Hide groups and user permission fields
        (_('Personal info'), {'fields': ('username', 'email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = ( # Set permissions when creating
        (None, {
            'fields': ('username', 'password1', 'password2', 'email', 'is_staff', 'is_superuser', 'group_set'),
        }),
    )

    add_form_template = 'admin/change_form.html'
    add_form = UserCreationFormExtended
    form = UserChangeFormExtended

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('group_set')


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'permission', 'tournament')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament')


User = get_user_model()
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
