"""Request/file-scoped participant references, never persisted in wizard sessions."""

from collections import defaultdict

from django.utils.functional import cached_property

from participants.models import Institution, Speaker, Team


class ImportReferences:
    def __init__(self, tournament):
        self.tournament = tournament

    @cached_property
    def institutions(self):
        return list(Institution.objects.all())

    @cached_property
    def institution_choices(self):
        return [(institution.pk, f'{institution.name} ({institution.code})') for institution in self.institutions]

    @cached_property
    def institutions_by_id(self):
        return {institution.pk: institution for institution in self.institutions}

    @cached_property
    def institution_names(self):
        names = defaultdict(dict)
        for institution in self.institutions:
            for value in (institution.name, institution.code):
                names[value][institution.pk] = institution
        return names

    def lookup_institution(self, value):
        matches = list(self.institution_names.get(value, {}).values())
        if not matches:
            raise Institution.DoesNotExist(f'Institution matching {value!r} does not exist.')
        if len(matches) > 1:
            raise Institution.MultipleObjectsReturned(f'Multiple institutions match {value!r}.')
        return matches[0]

    @cached_property
    def teams(self):
        return list(Team.objects.all_with_unconfirmed.filter(tournament=self.tournament).select_related('institution'))

    @cached_property
    def teams_by_id(self):
        return {team.pk: team for team in self.teams}

    @cached_property
    def team_identities(self):
        identities = defaultdict(list)
        for team in self.teams:
            identities[(team.institution_id, team.reference)].append(team)
        return identities

    @cached_property
    def speaker_names(self):
        return set(Speaker.objects.filter(team__tournament=self.tournament).values_list('team_id', 'name'))

    def lookup_team(self, institution, reference):
        matches = self.team_identities.get((institution.pk if institution else None, reference), [])
        if not matches:
            raise Team.DoesNotExist(f'Team matching {reference!r} does not exist.')
        if len(matches) > 1:
            raise Team.MultipleObjectsReturned(f'Multiple teams match {reference!r}.')
        return matches[0]
