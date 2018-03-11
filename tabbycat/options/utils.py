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
