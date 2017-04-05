from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from formtools.wizard.views import SessionWizardView

from participants.models import Adjudicator, Institution, Speaker, Team
from tournaments.mixins import TournamentMixin
from utils.mixins import PostOnlyRedirectView, SuperuserRequiredMixin
from utils.views import admin_required, expect_post, tournament_view
from venues.models import Venue, VenueCategory, VenueConstraint

from .forms import (AdjudicatorDetailsForm, ImportInstitutionsRawForm,
                    ImportVenuesRawForm, NumberForEachInstitutionForm,
                    TeamDetailsForm, VenueDetailsForm)


# TODO log actions for all of these?

class ImporterVisualIndexView(SuperuserRequiredMixin, TournamentMixin, TemplateView):
    template_name = 'visual_import_index.html'


class BaseImportWizardView(SuperuserRequiredMixin, TournamentMixin, SessionWizardView):
    """Common functionality for the import wizard views. In particular, this
    class implements functionality for a "details" step that is initialized
    with data from the previous step. The details step shows a ModelFormSet
    associated with a specified model."""

    DETAILS_STEP = 'details'
    tournament_redirect_pattern_name = 'importer-visual-index'

    model = None  # must be specified by subclass

    def get_details_form_initial(self):
        raise NotImplementedError

    def get_template_names(self):
        return ['visual_import_%(model)ss_%(step)s.html' % {
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
        instances = form_dict[self.DETAILS_STEP].save()
        messages.success(self.request, _("Added %(count)d %(model_plural)s.") % {
                'count': len(instances), 'model_plural': self.model._meta.verbose_name_plural})
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


class ImportAdjudicatorsWizardView(BaseImportByInstitutionWizardView):
    model = Adjudicator
    form_list = [
        ('numbers', NumberForEachInstitutionForm),
        ('details', modelformset_factory(Adjudicator, form=AdjudicatorDetailsForm, extra=0)),
    ]

    def get_details_instance_initial(self, i):
        return {'name': _("Adjudicator %(number)d") % {'number': i}, 'test_score': 2.5}


# ==============================================================================
# Old forms
# ==============================================================================

@admin_required
@tournament_view
def data_index(request, t):
    return render(request, 'data_index.html')


def enforce_length(value, type, model, request, extra_limit=0):
    # Used to check and truncate name lengths as needed
    max_length = model._meta.get_field(type).max_length
    if len(value) > max_length - extra_limit:
        messages.warning(request, "%s %s's name was too long so it \
            was truncated to the %s character limit" % (model.__name__, value, max_length))
        value = value[:max_length - extra_limit]
    return value


# ==============================================================================
# Institutions
# ==============================================================================


@admin_required
@tournament_view
def add_institutions(request, t):
    return render(request, 'add_institutions.html')


@admin_required
@expect_post
@tournament_view
def edit_institutions(request, t):
    institutions = []
    institution_lines = request.POST['institutions_raw'].rstrip().split('\n')
    for line in institution_lines:
        if "," not in line or line.split(',')[1].strip() == "":
            messages.error(request, "Institution '%s' could not be processed \
                because it did not have a code" % line)
            continue

        full_name = line.split(',')[0].strip()
        full_name = enforce_length(full_name, 'name', Institution, request)
        short_name = line.split(',')[1].strip()
        short_name = enforce_length(short_name, 'code', Institution, request)

        institution = Institution(name=full_name, code=short_name)
        institutions.append(institution)

    if len(institutions) == 0:
        messages.warning(request, "No institutions were added")
        return render(request, 'data_index.html')
    else:
        max_name = Institution._meta.get_field('name').max_length - 1
        max_code = Institution._meta.get_field('code').max_length - 1
        return render(request, 'edit_institutions.html', dict(
                      institutions=institutions,
                      full_name_max=max_name, code_max=max_code))


@admin_required
@expect_post
@tournament_view
def confirm_institutions(request, t):
    institution_names = request.POST.getlist('institution_names')
    institution_codes = request.POST.getlist('institution_codes')
    added_institutions = 0

    for i, key in enumerate(institution_names):
        try:
            full_name = institution_names[i]
            short_name = institution_codes[i]
            institution = Institution(name=full_name, code=short_name)
            institution.save()
            added_institutions += 1
        except IntegrityError:
            messages.error(request, "Institution '%s' already exists" % institution_names[i])

    if added_institutions > 0:
        messages.success(request, "%s Institutions have been added" % len(institution_names))

    return render(request, 'data_index.html')


# ==============================================================================
# Venues
# ==============================================================================

@admin_required
@tournament_view
def add_venues(request, t):
    return render(request, 'add_venues.html')


@admin_required
@expect_post
@tournament_view
def edit_venues(request, t):
    venues = []
    venue_lines = request.POST['venues_raw'].rstrip().split('\n')
    for line in venue_lines:
        # Sometimes people enter in the lists without a set priority
        if "," in line:
            name = line.split(',')[0].strip()
        else:
            name = line.strip()
        if name:
            name = enforce_length(name, 'name', Venue, request)
        else:
            continue

        # Allow people to not specify a priority when copy pasting
        if "," in line:
            priority = line.split(',')[1].strip()
        else:
            priority = 100
        if not priority:
            priority = 100

        if len(line.split(',')) > 2:
            category = line.split(',')[2].strip()
            venues.append({'name': name, 'priority': priority, 'category': category})
        else:
            venues.append({'name': name, 'priority': priority})

    if len(venues) == 0:
        messages.error(request, "No data was entered was entered in the form")
        return render(request, 'data_index.html')
    else:
        return render(request, 'edit_venues.html', dict(venues=venues,
                  max_name_length=Venue._meta.get_field('name').max_length - 1))


@admin_required
@expect_post
@tournament_view
def confirm_venues(request, t):
    venue_names = request.POST.getlist('venue_names')
    venue_priorities = request.POST.getlist('venue_priorities')
    venue_categories = request.POST.getlist('venue_categories')
    category_displays = request.POST.getlist('category_displays')
    venue_shares = request.POST.getlist('venue_shares')

    for i, key in enumerate(venue_names):
        venue_tournament = t
        if venue_shares[i] == "yes":
            venue_tournament = None

        priority = venue_priorities[i]
        if not priority or not float(priority).is_integer():
            messages.warning(request, "Venue %s could not be saved because \
                it did not have a valid priority number" % venue_names[i])
            continue

        venue = Venue(name=venue_names[i], priority=venue_priorities[i],
                      tournament=venue_tournament)
        venue.save()

        if venue_categories[i]:
            display = VenueCategory.DISPLAY_NONE
            try:
                if category_displays[i] == "prefix":
                    display = VenueCategory.DISPLAY_PREFIX
                elif category_displays[i] == "suffix":
                    display = VenueCategory.DISPLAY_SUFFIX
            except IndexError:
                pass

            try:
                venue_category = VenueCategory.objects.get(name=venue_categories[i])
            except VenueCategory.DoesNotExist:
                venue_category = VenueCategory(name=venue_categories[i],
                                               display_in_venue_name=display)
                venue_category.save()

            venue_category.venues.add(venue)
            venue_category.save()

    messages.success(request, "%s Venues have been added" % len(venue_names))
    return render(request, 'data_index.html')


# ==============================================================================
# Teams
# ==============================================================================

@admin_required
@tournament_view
def add_teams(request, t):
    institutions = Institution.objects.all()
    return render(request, 'add_teams.html', dict(institutions=institutions))


@admin_required
@expect_post
@tournament_view
def edit_teams(request, t):
    institutions_with_team_numbers = []

    # Set default speaker text to match tournament setup
    default_speakers = ""
    for i in range(1, t.pref('substantive_speakers') + 1):
        if i > 1:
            default_speakers += ","
        default_speakers += "Speaker %s" % i

    for pk, quantity in request.POST.items():
        if quantity:
            desired_teams_count = int(quantity) + 1  # +1 to 1-index team names
            institution = Institution.objects.get(id=pk)
            team_names = Team.objects.filter(
                institution=institution, tournament=t).values_list(
                'reference', flat=True).order_by('reference')
            available_team_numbers = []

            name_to_check = 1
            while name_to_check < desired_teams_count:
                # Check if the team name/number already exists
                if str(name_to_check) in team_names:
                    desired_teams_count += 1
                else:
                    available_team_numbers.append(name_to_check)

                name_to_check += 1

            institutions_with_team_numbers.append({
                'name': institution.name,
                'id': institution.id,
                'available_team_numbers': available_team_numbers
            })

    return render(request, 'edit_teams.html',
                  dict(institutions=institutions_with_team_numbers,
                       default_speakers=default_speakers,
                       max_name_length=Team._meta.get_field('reference').max_length - 1))


@admin_required
@expect_post
@tournament_view
def confirm_teams(request, t):
    sorted_post = sorted(request.POST.items())
    added_teams = 0

    for i in range(0, len(sorted_post) - 1, 4):
        # Sort through the items advancing 4 at a time
        instititution_id = sorted_post[i][1]
        team_name = sorted_post[i + 1][1]
        team_name = enforce_length(team_name, 'reference', Team, request)
        use_prefix = False

        if (sorted_post[i + 2][1] == "yes"):
            use_prefix = True
        speaker_names = sorted_post[i + 3][1].split(',')

        institution = Institution.objects.get(id=instititution_id)
        if team_name and speaker_names and institution:
            extra_reference_limit = 0
            extra_short_reference_limit = 0
            if use_prefix:
                # Team references/short_references depend on institution names
                extra_reference_limit = len(institution.name)
                extra_short_reference_limit = len(institution.code)

            reference = enforce_length(team_name, 'reference', Team, request, extra_limit=extra_reference_limit)
            short_reference = enforce_length(team_name, 'short_reference', Team, request, extra_limit=extra_short_reference_limit)

            newteam = Team(institution=institution,
                           reference=reference,
                           short_reference=short_reference,
                           tournament=t,
                           use_institution_prefix=use_prefix)
            try:
                newteam.save()
                for speaker in speaker_names:
                    name = enforce_length(speaker, 'name', Speaker, request)
                    newspeaker = Speaker(name=name, team=newteam)
                    newspeaker.save()
                added_teams += 1
            except IntegrityError:
                messages.error(request, "Team '%s %s' Was not saved; probably because that team already exists." % (institution, team_name))

    if added_teams > 0:
        messages.success(request, "%s Teams have been added" % int((len(sorted_post) - 1) / 4))
    return render(request, 'data_index.html')


# ==============================================================================
# Adjudicators
# ==============================================================================

@admin_required
@tournament_view
def add_adjudicators(request, t):
    institutions = Institution.objects.all()
    return render(request, 'add_adjudicators.html', dict(institutions=institutions))


@admin_required
@expect_post
@tournament_view
def edit_adjudicators(request, t):
    institutions = {}
    for pk, quantity in request.POST.items():
        if quantity:
            # Create a placeholder for loop
            institutions[pk] = list(range(1, int(quantity) + 1))

    context = {
        'institutions': institutions,
        'score_avg': round((t.pref('adj_max_score') + t.pref('adj_min_score')) / 2, 1),
        'max_name_length': Adjudicator._meta.get_field('name').max_length
    }
    return render(request, 'edit_adjudicators.html', context)


@admin_required
@expect_post
@tournament_view
def confirm_adjudicators(request, t):
    sorted_post = sorted(request.POST.items())

    for i in range(0, len(sorted_post), 4):
        # Sort through the items advancing 4 at a time
        adj_institution = Institution.objects.get(id=sorted_post[i][1])
        adj_name = sorted_post[i + 1][1]
        adj_name = enforce_length(adj_name, 'name', Adjudicator, request)
        adj_rating = sorted_post[i + 2][1]
        adj_shared = sorted_post[i + 3][1]

        if adj_shared == "yes":
            adj_t = None
        else:
            adj_t = t

        if adj_name and adj_rating and adj_institution:
            newadj = Adjudicator(institution=adj_institution,
                                 name=adj_name, tournament=adj_t,
                                 test_score=adj_rating)
            newadj.save()

    messages.success(request, "%s Adjudicators have been added" % int((len(sorted_post) - 1) / 3))
    return render(request, 'data_index.html')


# ==============================================================================
# Importing Shared
# ==============================================================================

class ConfirmDataView(TournamentMixin, SuperuserRequiredMixin, PostOnlyRedirectView):
    tournament_redirect_pattern_name = 'data_index'


# ==============================================================================
# Importing Venue Category Constraints
# ==============================================================================

class AddConstraintsView(TournamentMixin, SuperuserRequiredMixin, TemplateView):
    template_name = 'add_constraints.html'
    type = None

    def get_context_data(self, **kwargs):
        kwargs["entities"] = self.type.objects.all()
        kwargs["entity_type"] = self.type.__name__
        return super().get_context_data(**kwargs)


class EditConstraintsView(TournamentMixin, SuperuserRequiredMixin, TemplateView):
    template_name = 'edit_constraints.html'
    type = None

    def post(self, request, *args, **kwargs):
        venue_categories = VenueCategory.objects.all()
        entities = []
        for entity_id, checked in request.POST.items():
            entity = self.type.objects.get(pk=entity_id)
            entity.constraints = []

            for venue_category in venue_categories:
                # Find all constraints matching this entity
                content_type = ContentType.objects.get_for_model(self.type)
                constraint = VenueConstraint.objects.filter(
                    category=venue_category,
                    subject_content_type=content_type,
                    subject_id=entity_id).first()

                # Prepopulate priority data (because we are wiping each time)
                entity.constraints.append({
                    'id': venue_category.id,
                    'name': venue_category.name,
                    'priority': constraint.priority if constraint else ''
                })

            entities.append(entity)

        context = self.get_context_data(entities)
        return super(TemplateView, self).render_to_response(context)

    def get_context_data(self, entities, **kwargs):
        kwargs["venue_categories"] = VenueCategory.objects.all()
        kwargs["entities"] = entities
        kwargs["entity_type"] = self.type.__name__
        return super().get_context_data(**kwargs)


class ConfirmConstraintsView(ConfirmDataView):
    type = None

    def post(self, request, *args, **kwargs):
        # Delete existing constraints for this type
        for entity_id in request.POST.getlist('entityIDs'):
            entity = self.type.objects.get(pk=entity_id)
            content_type = ContentType.objects.get_for_model(self.type)
            VenueConstraint.objects.filter(subject_content_type=content_type,
                                           subject_id=entity_id).delete()

        venue_priorities = request.POST.dict()
        del venue_priorities["entityIDs"]

        created_constraints = 0
        print(venue_priorities.items())

        for idset, priority in venue_priorities.items():
            entity_id = idset.split('_')[0]
            venue_category_id = idset.split('_')[1]
            print('have a idset', idset, ' priority ', priority)

            if entity_id and venue_category_id and priority:
                entity = self.type.objects.get(pk=int(entity_id))
                category = VenueCategory.objects.get(pk=int(venue_category_id))
                VenueConstraint(subject=entity, priority=priority,
                                category=category).save()
                created_constraints += 1

        messages.success(request, "%s Venue Constraints for %ss have been added" %
                                  (created_constraints, self.type.__name__))
        return super().post(request, *args, **kwargs)
