import logging

logger = logging.getLogger(__name__)


def use_team_code_names(tournament, admin):
    """Returns True if team code names should be used, given the tournament
    preferences of `tournament` and whether the request is for an admin view.
    `admin` should be True if the request is for an admin view and False if not.
    """
    if tournament.pref('team_code_names') in ['admin-tooltips-real', 'everywhere']:
        return True
    if tournament.pref('team_code_names') == 'admin-tooltips-code' and not admin:
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
    else:
        logger.error("Unrecognized team code name preference: %s", pref)
        return 'code'
