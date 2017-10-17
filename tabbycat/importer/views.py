import logging
from smtplib import SMTPException

from django.contrib import messages
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.views.generic import TemplateView

from formtools.wizard.views import SessionWizardView

from participants.emoji import set_emoji
from participants.models import Adjudicator, Institution, Speaker, Team
from tournaments.mixins import TournamentMixin
from utils.misc import reverse_tournament
from utils.mixins import SuperuserRequiredMixin
from utils.tables import TabbycatTableBuilder
from utils.urlkeys import populate_url_keys
from utils.views import PostOnlyRedirectView, VueTableTemplateView
from venues.models import Venue

from .forms import (AdjudicatorDetailsForm, ImportInstitutionsRawForm,
                    ImportVenuesRawForm, NumberForEachInstitutionForm,
                    TeamDetailsForm, TeamDetailsFormSet, VenueDetailsForm)
from .utils import send_randomised_url_emails

logger = logging.getLogger(__name__)


# TODO: add log actions for all of these?

class ImporterSimpleIndexView(SuperuserRequiredMixin, TournamentMixin, TemplateView):
    template_name = 'simple_import_index.html'


class BaseImportWizardView(SuperuserRequiredMixin, TournamentMixin, SessionWizardView):
    """Common functionality for the import wizard views. In particular, this
    class implements functionality for a "details" step that is initialized
    with data from the previous step. The details step shows a ModelFormSet
    associated with a specified model."""

    DETAILS_STEP = 'details'
    tournament_redirect_pattern_name = 'importer-simple-index'

    model = None  # must be specified by subclass

    def get_details_form_initial(self):
        raise NotImplementedError

    def get_template_names(self):
        return ['simple_import_%(model)ss_%(step)s.html' % {
            'model': self.model._meta.model_name,
            'step': self.steps.current
        }]

    def get_form_initial(self, step):
        """Overridden to initialize the 'details' step with data from a previous
        step."""
        if step == self.DETAILS_STEP and step == self.steps.next:
            return self.get_details_form_initial()
        else:
            return super().get_form_initial(step)

    def get_form_instance(self, step):
        if step == self.DETAILS_STEP:
            return self.model.objects.none()
        else:
            return super().get_form_instance(step)

    def get_form(self, step=None, **kwargs):
        form = super().get_form(step, **kwargs)
        if step == self.DETAILS_STEP:
            form.extra = len(form.initial_extra)
            form.save_as_new = True
        return form

    def done(self, form_list, form_dict, **kwargs):
        self.instances = form_dict[self.DETAILS_STEP].save()
        messages.success(self.request, _("Added %(count)d %(model_plural)s.") % {
                'count': len(self.instances), 'model_plural': self.model._meta.verbose_name_plural})
        return HttpResponseRedirect(self.get_redirect_url())


class ImportInstitutionsWizardView(BaseImportWizardView):
    model = Institution
    form_list = [
        ('raw', ImportInstitutionsRawForm),
        ('details', modelformset_factory(Institution, fields=('name', 'code'), extra=0)),
    ]

    def get_details_form_initial(self):
        return self.get_cleaned_data_for_step('raw')['institutions_raw']


class ImportVenuesWizardView(BaseImportWizardView):
    model = Venue
    form_list = [
        ('raw', ImportVenuesRawForm),
        ('details', modelformset_factory(Venue, form=VenueDetailsForm, extra=0))
    ]

    def get_form_kwargs(self, step):
        if step == 'details':
            return {'form_kwargs': {'tournament': self.get_tournament()}}
        else:
            return super().get_form_kwargs(step)

    def get_details_form_initial(self):
        return self.get_cleaned_data_for_step('raw')['venues_raw']


class BaseImportByInstitutionWizardView(BaseImportWizardView):
    """Common functionality in teams and institutions wizards."""

    def get_form_kwargs(self, step):
        if step == 'numbers':
            return {'institutions': Institution.objects.all()}
        elif step == 'details':
            return {'form_kwargs': {'tournament': self.get_tournament()}}

    def get_details_form_initial(self):
        data = self.get_cleaned_data_for_step('numbers')
        initial_list = []
        for institution in Institution.objects.order_by('name'):
            number = data.get('number_institution_%d' % institution.id, 0)
            if number is None: # field left blank
                continue
            for i in range(1, number+1):
                initial = {'institution': institution.id}
                initial.update(self.get_details_instance_initial(i))
                initial_list.append(initial)
        return initial_list

    def get_details_instance_initial(self):
        raise NotImplementedError


class ImportTeamsWizardView(BaseImportByInstitutionWizardView):
    model = Team
    form_list = [
        ('numbers', NumberForEachInstitutionForm),
        ('details', modelformset_factory(Team, form=TeamDetailsForm, formset=TeamDetailsFormSet, extra=0)),
    ]

    def get_details_instance_initial(self, i):
        return {'reference': str(i), 'use_institution_prefix': True}

    def done(self, form_list, form_dict, **kwargs):
        # Also set emoji on teams
        redirect = super().done(form_list, form_dict, **kwargs)
        set_emoji(self.instances, self.get_tournament())
        return redirect


class ImportAdjudicatorsWizardView(BaseImportByInstitutionWizardView):
    model = Adjudicator
    form_list = [
        ('numbers', NumberForEachInstitutionForm),
        ('details', modelformset_factory(Adjudicator, form=AdjudicatorDetailsForm, extra=0)),
    ]

    def get_details_instance_initial(self, i):
        return {'name': _("Adjudicator %(number)d") % {'number': i}, 'test_score': 2.5}


# ==============================================================================
# Randomised URL creation
# ==============================================================================

class RandomisedUrlsMixin(TournamentMixin):

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        kwargs['exists'] = tournament.adjudicator_set.filter(url_key__isnull=False).exists() or \
            tournament.team_set.filter(url_key__isnull=False).exists()
        kwargs['blank_exists'] = tournament.adjudicator_set.filter(url_key__isnull=True).exists() or \
            tournament.team_set.filter(url_key__isnull=True).exists()
        return super().get_context_data(**kwargs)


class RandomisedUrlsView(RandomisedUrlsMixin, SuperuserRequiredMixin, VueTableTemplateView):

    template_name = 'randomised_urls.html'
    tables_orientation = 'columns'

    def get_teams_table(self):
        tournament = self.get_tournament()

        def _build_url(team):
            if team.url_key is None:
                return {'text': _("no URL"), 'class': 'text-warning'}
            path = reverse_tournament('adjfeedback-public-add-from-team-randomised', tournament,
                kwargs={'url_key': team.url_key})
            return {'text': self.request.build_absolute_uri(path), 'class': 'small'}

        teams = tournament.team_set.all()
        table = TabbycatTableBuilder(view=self, title=_("Teams"), sort_key=_("Team"))
        table.add_team_columns(teams)
        table.add_column(_("Feedback URL"), [_build_url(team) for team in teams])

        return table

    def get_adjudicators_table(self):
        tournament = self.get_tournament()

        def _build_url(adjudicator, url_name):
            if adjudicator.url_key is None:
                return {'text': _("no URL"), 'class': 'text-warning'}
            path = reverse_tournament(url_name, tournament, kwargs={'url_key': adjudicator.url_key})
            return {'text': self.request.build_absolute_uri(path), 'class': 'small'}

        adjudicators = Adjudicator.objects.all() if tournament.pref('share_adjs') else tournament.adjudicator_set.all()
        table = TabbycatTableBuilder(view=self, title=_("Adjudicators"), sort_key=_("Name"))
        table.add_adjudicator_columns(adjudicators, hide_institution=True, hide_metadata=True)
        table.add_column(_("Feedback URL"), [_build_url(adj, 'adjfeedback-public-add-from-adjudicator-randomised') for adj in adjudicators])
        table.add_column(_("Ballot URL"), [_build_url(adj, 'results-public-ballotset-new-randomised') for adj in adjudicators])

        return table

    def get_tables(self):
        return [self.get_adjudicators_table(), self.get_teams_table()]


class GenerateRandomisedUrlsView(SuperuserRequiredMixin, TournamentMixin, PostOnlyRedirectView):

    tournament_redirect_pattern_name = 'randomised-urls-view'

    def post(self, request, *args, **kwargs):
        tournament = self.get_tournament()

        nexisting_adjs = tournament.adjudicator_set.filter(url_key__isnull=False).count()
        nexisting_teams = tournament.team_set.filter(url_key__isnull=False).count()
        blank_adjs = tournament.adjudicator_set.filter(url_key__isnull=True)
        blank_teams = tournament.team_set.filter(url_key__isnull=True)
        nblank_adjs = blank_adjs.count()
        nblank_teams = blank_teams.count()

        if nblank_adjs == 0 and nblank_teams == 0:
            messages.error(self.request, _("All adjudicators and teams already have private URLs. "
                "If you want to delete them, use the Edit Database area."))

        else:
            populate_url_keys(blank_adjs)
            populate_url_keys(blank_teams)

            if nexisting_adjs == 0 and nexisting_teams == 0:
                # too hard to pluralize, will do it when we hit a language that actually needs it
                messages.success(self.request, _("Private URLs were generated for all %(nblank_adjs)d "
                    "adjudicators and all %(nblank_teams)d teams.") % {
                    'nblank_adjs': nblank_adjs, 'nblank_teams': nblank_teams,
                })
            else:
                # too hard to pluralize, will do it when we hit a language that actually needs it
                messages.success(self.request, _("Private URLs were generated for %(nblank_adjs)d "
                    "adjudicators and %(nblank_teams)d teams. The already-existing private URLs for "
                    "%(nexisting_adjs)d adjudicators and %(nexisting_teams)d teams were left intact.") % {
                    'nblank_adjs': nblank_adjs, 'nblank_teams': nblank_teams,
                    'nexisting_adjs': nexisting_adjs, 'nexisting_teams': nexisting_teams,
                })

        return super().post(request, *args, **kwargs)


class BaseEmailRandomisedUrlsView(RandomisedUrlsMixin, VueTableTemplateView):

    tables_orientation = 'rows'

    def get_context_data(self, **kwargs):
        kwargs['url_type'] = self.url_type

        kwargs['adjudicators_no_email'] = self.get_tournament().adjudicator_set.filter(
            url_key__isnull=False, email__isnull=True
        ).values_list('name', flat=True)
        return super().get_context_data(**kwargs)

    def get_adjudicators_table(self, url_name, url_header):
        tournament = self.get_tournament()

        def _build_url(adjudicator):
            path = reverse_tournament(url_name, tournament, kwargs={'url_key': adjudicator.url_key})
            return self.request.build_absolute_uri(path)

        adjudicators = Adjudicator.objects.filter(tournament=tournament,
                url_key__isnull=False, email__isnull=False)
        title = _("Adjudicators who will be sent e-mails (%(n)s)") % {'n': adjudicators.count()}
        table = TabbycatTableBuilder(view=self, title=title, sort_key=_("Name"))
        table.add_adjudicator_columns(adjudicators, hide_institution=True, hide_metadata=True)
        table.add_column(_("Email"), [adj.email for adj in adjudicators])
        table.add_column(url_header, [_build_url(adj) for adj in adjudicators])

        return table


class EmailBallotUrlsView(BaseEmailRandomisedUrlsView):

    template_name = 'ballot_urls_email_list.html'
    url_type = 'ballot'

    def get_table(self):
        return self.get_adjudicators_table('results-public-ballotset-new-randomised', _("Ballot URL"))


class EmailFeedbackUrlsView(BaseEmailRandomisedUrlsView):

    template_name = 'feedback_urls_email_list.html'
    url_type = 'feedback'

    def get_context_data(self, **kwargs):
        kwargs['speakers_no_email'] = Speaker.objects.filter(team__tournament=self.get_tournament(),
            team__url_key__isnull=False, email__isnull=True).values_list('name', flat=True)
        return super().get_context_data(**kwargs)

    def get_speakers_table(self):
        tournament = self.get_tournament()

        def _build_url(speaker):
            path = reverse_tournament('adjfeedback-public-add-from-team-randomised', tournament,
                kwargs={'url_key': speaker.team.url_key})
            return self.request.build_absolute_uri(path)

        speakers = Speaker.objects.filter(team__tournament=tournament,
                team__url_key__isnull=False, email__isnull=False)
        title = _("Speakers who will be sent e-mails (%(n)s)") % {'n': speakers.count()}
        table = TabbycatTableBuilder(view=self, title=title, sort_key=_("Team"))
        table.add_speaker_columns(speakers, categories=False)
        table.add_team_columns([speaker.team for speaker in speakers])
        table.add_column(_("Email"), [speaker.email for speaker in speakers])
        table.add_column(_("Feedback URL"), [_build_url(speaker) for speaker in speakers])

        return table

    def get_tables(self):
        speaker_table = self.get_speakers_table()
        adjudicator_table = self.get_adjudicators_table(
                'adjfeedback-public-add-from-adjudicator-randomised', _("Feedback URL"))
        return [speaker_table, adjudicator_table]


class BaseConfirmEmailRandomisedUrlsView(SuperuserRequiredMixin, TournamentMixin, PostOnlyRedirectView):

    tournament_redirect_pattern_name = 'randomised-urls-view'


class ConfirmEmailBallotUrlsView(BaseConfirmEmailRandomisedUrlsView):

    def post(self, request, *args, **kwargs):

        tournament = self.get_tournament()

        subject = _("Your personal ballot submission URL for %(tournament)s")
        message = _(
            "Hi %(name)s,\n\n"
            "At %(tournament)s, we are using an online ballot system. You can submit "
            "your ballots at the following URL. This URL is unique to you — do not share it with "
            "anyone, as anyone who knows it can submit ballots on your team's behalf. This URL "
            "will not change throughout this tournament, so we suggest bookmarking it.\n\n"
            "Your personal private ballot submission URL is:\n"
            "%(url)s"
        )
        adjudicators = tournament.adjudicator_set.filter(
                url_key__isnull=False, email__isnull=False)

        try:
            nadjudicators = send_randomised_url_emails(
                request, tournament, adjudicators,
                'results-public-ballotset-new-randomised',
                lambda adj: adj.url_key,
                subject, message
            )
        except SMTPException:
            messages.error(request, _("There was a problem sending private ballot URLs to adjudicators."))
        else:
            messages.success(request, ungettext(
                "E-mails with private ballot URLs were sent to %(nadjudicators)d adjudicator.",
                "E-mails with private ballot URLs were sent to %(nadjudicators)d adjudicators.",
                nadjudicators
            ) % {'nadjudicators': nadjudicators})

        return super().post(request, *args, **kwargs)


class ConfirmEmailFeedbackUrlsView(BaseConfirmEmailRandomisedUrlsView):

    def post(self, request, *args, **kwargs):

        tournament = self.get_tournament()
        success = True

        subject = _("Your team's feedback submission URL for %(tournament)s")
        message = _(
            "Hi %(name)s,\n\n"
            "At %(tournament)s, we are using an online adjudicator feedback system. As part of "
            "%(team)s, you can submit your feedback at the following URL. This URL is unique "
            "to you — do not share it with anyone, as anyone who knows it can submit feedback on "
            "your team's behalf. This URL will not change throughout this tournament, so we "
            "suggest bookmarking it.\n\n"
            "Your team's private feedback submission URL is:\n"
            "%(url)s"
        )
        speakers = Speaker.objects.filter(team__tournament=tournament,
                team__url_key__isnull=False, email__isnull=False)

        try:
            nspeakers = send_randomised_url_emails(
                request, tournament, speakers,
                'adjfeedback-public-add-from-team-randomised',
                lambda speaker: speaker.team.url_key,
                subject, message
            )
        except SMTPException:
            messages.error(request, _("There was a problem sending private feedback URLs to speakers."))
            success = False

        subject = _("Your personal feedback submission URL for %(tournament)s")
        message = _(
            "Hi %(name)s,\n\n"
            "At %(tournament)s, we are using an online adjudicator feedback system. You can submit "
            "your feedback at the following URL. This URL is unique to you — do not share it with "
            "anyone, as anyone who knows it can submit feedback on your team's behalf. This URL "
            "will not change throughout this tournament, so we suggest bookmarking it.\n\n"
            "Your personal private feedback submission URL is:\n"
            "%(url)s"
        )
        adjudicators = tournament.adjudicator_set.filter(
                url_key__isnull=False, email__isnull=False)

        try:
            nadjudicators = send_randomised_url_emails(
                request, tournament, adjudicators,
                'adjfeedback-public-add-from-adjudicator-randomised',
                lambda adj: adj.url_key,
                subject, message
            )
        except SMTPException:
            messages.error(request, _("There was a problem sending private feedback URLs to adjudicators."))
            success = False

        if success:
            # Translators: This goes in the "speakers_phrase" variable in "E-mails with private feedback URLs were sent..."
            speakers_phrase = ungettext("%(nspeakers)d speaker",
                "%(nspeakers)d speakers", nspeakers) % {'nspeakers': nspeakers}
            # Translators: This goes in the "adjudicators_phrase" variable in "E-mails with private feedback URLs were sent..."
            adjudicators_phrase = ungettext("%(nadjudicators)d adjudicator",
                "%(nadjudicators)d adjudicators", nadjudicators) % {'nadjudicators': nadjudicators}
            messages.success(request, _("E-mails with private feedback URLs were sent to "
                "%(speakers_phrase)s and %(adjudicators_phrase)s") % {
                'speakers_phrase': speakers_phrase, 'adjudicators_phrase': adjudicators_phrase
            })

        return super().post(request, *args, **kwargs)
