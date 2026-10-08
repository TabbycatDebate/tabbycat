import logging

from django.contrib.auth.models import AnonymousUser
from django.forms import ValidationError
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from users.permissions import has_permission, Permission

logger = logging.getLogger(__name__)


def use_team_code_names(tournament, admin, user=AnonymousUser()):
    """Returns True if team code names should be used, given the tournament
    preferences of `tournament` and whether the request is for an admin view.
    `admin` should be True if the request is for an admin view and False if not.
    """
    if tournament.pref('team_code_names') in ['admin-tooltips-real', 'everywhere']:
        return True
    if tournament.pref('team_code_names') == 'admin-tooltips-code' and not (admin and has_permission(user, Permission.VIEW_DECODED_TEAMS, tournament)):
        return True
    return False


def use_team_code_names_data_entry(tournament, tabroom):
    """Returns one of 'off', 'code' and 'both', indicating whether code names
    should (respectively) not be used, only be used, or be used alongside real
    names, in data entry screens. This is a different use-case from
    use_team_code_names() above, because during data entry, the paper ballots
    will have code names on them, so it's easier for data entry staff to look
    at them by code name."""
    pref = tournament.pref('team_code_names')
    if pref in ['off', 'all-tooltips']:
        return 'off'
    elif pref in ['admin-tooltips-code', 'admin-tooltips-real']:
        return 'both' if tabroom else 'code'
    elif pref == 'everywhere':
        return 'code'


def validate_metric_duplicates(generator, value):
    # Check that non-repeatable metrics aren't listed twice. Score criterion
    # metrics aren't in metric_annotator_classes (they're built per-tournament),
    # and are never repeatable, so check those by key.
    classes = []
    criterion_keys = []
    for metric in value:
        klass = generator.metric_annotator_classes.get(metric)
        if klass is None:
            criterion_keys.append(metric)
        else:
            classes.append(klass)

    duplicates = [c for c in classes if not c.repeatable and classes.count(c) > 1]
    duplicates_str = list({force_str(c.name) for c in duplicates})
    duplicates_str += list({k for k in criterion_keys if criterion_keys.count(k) > 1})
    if duplicates_str:
        raise ValidationError(_("The following metrics can't be listed twice: "
                "%(duplicates)s") % {'duplicates': ", ".join(duplicates_str)})
