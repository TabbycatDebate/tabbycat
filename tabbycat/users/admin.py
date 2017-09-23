from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _


# ==============================================================================
# Authentication and Authorization
# ==============================================================================

admin.site.unregister(Group) # No need to show groups


class CustomUserLabelsMixin():
    def __init__(self, *args, **kwargs):
        super(CustomUserLabelsMixin, self).__init__(*args, **kwargs)
        self.fields['is_staff'].label = _("Tab Assistant")
        self.fields['is_staff'].help_text = _("Tab Assistant's can perform "
            "data-entry tasks such as adding ballots, feedback, etc but cannot "
            "access confidential areas or perform the tasks necessary to run a "
            "tournament such as creating rounds, viewing feedback, etc.")
        self.fields['is_superuser'].label = _("Tab Director")
        self.fields['is_superuser'].help_text = _("Tab Director's have full "
            "access all areas necessary to run a tournament. Often members of "
            "the adjudication core are set as Tab Directors so they can more "
            "easily view confidential areas such as Feedback and Standings. "
            "Shown as 'Superuser Status' in the Users list.")


class UserChangeFormFormExtended(CustomUserLabelsMixin, UserChangeForm):
    pass


class UserCreationFormExtended(CustomUserLabelsMixin, UserCreationForm):
    pass


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'is_superuser')

    fieldsets = ( # Hide groups and user permission fields
        ('Personal info', {'fields': ('username', 'email', 'password')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = ( # Set permissions when creating
        (None, {
            'fields': ('username', 'password1', 'password2', 'is_staff', 'is_superuser')
        }),
    )

    add_form = UserCreationFormExtended
    form = UserChangeFormFormExtended


User = get_user_model()
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
