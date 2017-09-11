import logging

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from formtools.wizard.views import SessionWizardView

from participants.emoji import set_emoji
from participants.models import Adjudicator, Institution, Speaker, Team
from tournaments.mixins import TournamentMixin
from utils.misc import reverse_tournament
from utils.mixins import SuperuserRequiredMixin
from utils.views import PostOnlyRedirectView
from utils.urlkeys import populate_url_keys
from venues.models import Venue

from .forms import (AdjudicatorDetailsForm, ImportInstitutionsRawForm,
                    ImportVenuesRawForm, NumberForEachInstitutionForm,
                    TeamDetailsForm, VenueDetailsForm)

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
        ('details', modelformset_factory(Team, form=TeamDetailsForm, extra=0)),
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

class RandomisedUrlsView(SuperuserRequiredMixin, TournamentMixin, TemplateView):

    template_name = 'randomised_urls.html'
    show_emails = False

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        kwargs['teams'] = tournament.team_set.all().order_by('short_name')
        if not tournament.pref('share_adjs'):
            kwargs['adjs'] = tournament.adjudicator_set.all().order_by('name')
        else:
            kwargs['adjs'] = Adjudicator.objects.all().order_by('name')
        kwargs['exists'] = tournament.adjudicator_set.filter(url_key__isnull=False).exists() or \
            tournament.team_set.filter(url_key__isnull=False).exists()
        kwargs['tournament_slug'] = tournament.slug
        return super().get_context_data(**kwargs)


class GenerateRandomisedUrlsView(SuperuserRequiredMixin, TournamentMixin, PostOnlyRedirectView):

    tournament_redirect_pattern_name = 'randomised-urls-view'

    def post(self, request, *args, **kwargs):
        tournament = self.get_tournament()

        # Only works if there are no randomised URLs now
        if tournament.adjudicator_set.filter(url_key__isnull=False).exists() or \
                tournament.team_set.filter(url_key__isnull=False).exists():
            messages.error(
                self.request, "There are already private URLs. " +
                "You must use the Django management commands to populate or " +
                "delete private URLs.")
        else:
            populate_url_keys(tournament.adjudicator_set.all())
            populate_url_keys(tournament.team_set.all())
            messages.success(self.request, "Private URLs were generated for all teams and adjudicators.")

        return super().post(request, *args, **kwargs)


class EmailRandomisedUrlsView(RandomisedUrlsView):

    show_emails = True
    template_name = 'randomised_urls_email_list.html'

    def get_context_data(self, **kwargs):
        kwargs['url_type'] = self.url_type
        return super().get_context_data(**kwargs)


class EmailBallotUrlsView(EmailRandomisedUrlsView):

    url_type = 'ballot'


class EmailFeedbackUrlsView(EmailRandomisedUrlsView):

    url_type = 'feedback'


class ConfirmEmailRandomisedUrlsView(SuperuserRequiredMixin, TournamentMixin, PostOnlyRedirectView):

    tournament_redirect_pattern_name = 'randomised-urls-view'

    def post(self, request, *args, **kwargs):

        tournament = self.get_tournament()
        speakers = Speaker.objects.filter(team__tournament=tournament,
            team__url_key__isnull=False, email__isnull=False)
        adjudicators = tournament.adjudicator_set.filter(
            url_key__isnull=False, email__isnull=False)

        if self.url_type is 'feedback':
            for speaker in speakers:
                if speaker.email is None:
                    continue

                team_path = reverse_tournament(
                    'adjfeedback-public-add-from-team-randomised',
                    tournament, kwargs={'url_key': speaker.team.url_key})
                team_link = self.request.build_absolute_uri(team_path)
                message = (''
                    'Hi %s, \n\n'
                    'At %s we are using an online feedback system. As part of %s '
                    'your team\'s feedback can be submitted at the following URL. '
                    'This URL is unique to you — do not share it as anyone with '
                    'this link can submit feedback on your team\s '
                    ' behalf. It will not change so we suggest bookmarking it. '
                    'The URL is: \n\n %s'
                     % (speaker.name, tournament.short_name,
                        speaker.team.short_name, team_link))

                try:
                    send_mail("Your Feedback URL for %s" % tournament.short_name,
                        message, settings.DEFAULT_FROM_EMAIL, [speaker.email],
                        fail_silently=False)
                    logger.info("Sent email with key to %s (%s)" % (speaker.email, speaker.name))
                except:
                    logger.info("Failed to send email to %s speaker.email")

        for adjudicator in adjudicators:
            if adjudicator.email is None:
                continue

            if self.url_type is 'feedback':
                adj_path = reverse_tournament(
                    'adjfeedback-public-add-from-adjudicator-randomised',
                    tournament, kwargs={'url_key': adjudicator.url_key})
            elif self.url_type is 'ballot':
                adj_path = reverse_tournament(
                    'results-public-ballotset-new-randomised',
                    tournament, kwargs={'url_key': adjudicator.url_key})

            adj_link = self.request.build_absolute_uri(adj_path)
            message = (''
                'Hi %s, \n\n'
                'At %s we are using an online %s system. Your %s '
                'can be submitted at the following URL. This URL is unique to '
                'you — do not share it as anyone with this link can submit '
                '%ss on your behalf. It will not change so we suggest '
                'bookmarking it. The URL is: \n\n %s'
                 % (adjudicator.name, tournament.short_name, self.url_type,
                    self.url_type, self.url_type, adj_link))

            try:
                send_mail("Your Feedback URL for %s" % tournament.short_name,
                    message, settings.DEFAULT_FROM_EMAIL, [adjudicator.email],
                    fail_silently=False)
                logger.info("Sent email with key to %s (%s)" % (adjudicator.email, adjudicator.name))
            except:
                logger.info("Failed to send email %s" % adjudicator.email)

        messages.success(self.request, "Emails were sent for all teams and adjudicators.")
        return super().post(request, *args, **kwargs)


class ConfirmEmailBallotUrlsView(ConfirmEmailRandomisedUrlsView):

    url_type = 'ballot'


class ConfirmEmailFeedbackUrlsView(ConfirmEmailRandomisedUrlsView):

    url_type = 'feedback'
