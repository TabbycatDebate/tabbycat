import random
from math import log10

from django import forms
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from options.preferences import MissingAdjudicatorRule
from participants.emoji import EMOJI_RANDOM_FIELD_CHOICES, pick_unused_emoji
from participants.models import Adjudicator, Coach, Institution, Speaker, Team, TournamentInstitution
from privateurls.utils import populate_url_keys

from .form_utils import CustomQuestionsFormMixin
from .models import LineItem, PriceItem
from .payment_utils import add_item


class TournamentInstitutionForm(CustomQuestionsFormMixin, forms.ModelForm):

    institution_name = Institution._meta.get_field('name')
    institution_code = Institution._meta.get_field('code')

    name = forms.CharField(max_length=institution_name.max_length, label=capfirst(institution_name.verbose_name), help_text=institution_name.help_text)
    code = forms.CharField(max_length=institution_code.max_length, label=capfirst(institution_code.verbose_name), help_text=institution_code.help_text)

    field_order = ('name', 'code', 'teams_requested', 'adjudicators_requested')

    def __init__(self, tournament, *args, **kwargs):
        self.tournament = tournament
        super().__init__(*args, **kwargs)
        self.add_question_fields()

        if not self.tournament.pref('reg_institution_slots'):
            self.fields.pop('teams_requested')
            self.fields.pop('adjudicators_requested')

    class Meta:
        model = TournamentInstitution
        exclude = ('tournament', 'institution', 'teams_allocated', 'adjudicators_allocated')

    def save(self):
        inst, created = Institution.objects.get_or_create(name=self.cleaned_data.pop('name'), code=self.cleaned_data.pop('code'))

        obj = super().save(commit=False)
        obj.institution = inst
        obj.tournament = self.tournament
        obj.save()
        self.save_answers(obj)

        return obj


class InstitutionCoachForm(CustomQuestionsFormMixin, forms.ModelForm):

    def __init__(self, tournament, *args, **kwargs):
        self.tournament = tournament
        super().__init__(*args, **kwargs)
        self.add_question_fields()

    class Meta:
        model = Coach
        fields = ('name', 'email')
        labels = {
            'name': _('Name of primary contact'),
        }

    def save(self):
        obj = super().save()
        populate_url_keys([obj])
        self.save_answers(obj)
        return obj


class TeamForm(CustomQuestionsFormMixin, forms.ModelForm):

    key = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, tournament, *args, institution=None, key=None, **kwargs):
        self.tournament = tournament
        self.institution = institution
        super().__init__(*args, **kwargs)

        self.fields['tournament'].initial = self.tournament
        if key:
            self.fields['key'].initial = key

        use_inst_field = self.fields['use_institution_prefix']
        use_inst_field.initial = bool(self.institution)

        if self.tournament.pref('team_name_generator') != 'user' and self.institution:
            self.fields.pop('reference')

        if not self.institution or 'use_institution_prefix' not in self.tournament.pref('reg_team_fields') or self.tournament.pref('team_name_generator') != 'user':
            use_inst_field.widget = forms.HiddenInput()

        for field in {'code_name', 'break_categories', 'seed', 'emoji'} - set(self.tournament.pref('reg_team_fields')):
            self.fields.pop(field)

        if self.institution is not None:
            self.fields['institution'].widget = forms.HiddenInput()
            self.fields['institution'].initial = self.institution

        if 'emoji' in self.fields:
            used_emoji = self.tournament.team_set.filter(emoji__isnull=False).values_list('emoji', flat=True)
            self.fields['emoji'].choices = [e for e in EMOJI_RANDOM_FIELD_CHOICES if e[0] not in used_emoji]
            self.fields['emoji'].initial = random.choice(self.fields['emoji'].choices)[0]

        if 'seed' in self.fields and self.tournament.pref('show_seed_in_importer') == 'title':
            self.fields['seed'] = forms.ChoiceField(required=False, label=self.fields['seed'].label, choices=(
                (0, _("Unseeded")),
                (1, _("Free seed")),
                (2, _("Half seed")),
                (3, _("Full seed")),
            ), help_text=self.fields['seed'].help_text)

        if 'break_categories' in self.fields:
            bcs = self.tournament.breakcategory_set.exclude(is_general=True)
            if len(bcs) == 0:
                self.fields.pop('break_categories')
            else:
                self.fields['break_categories'].queryset = bcs

        self.add_question_fields()

    class Meta:
        model = Team
        fields = ('tournament', 'reference', 'institution', 'use_institution_prefix', 'code_name', 'emoji', 'seed', 'break_categories')
        labels = {
            'reference': _("Team name (excluding institution)"),
        }
        widgets = {
            'tournament': forms.HiddenInput(),
        }

    def save(self):
        self.instance.tournament = self.tournament

        if self.institution:
            self.instance.institution = self.institution

        if 'use_institution_prefix' not in self.tournament.pref('reg_team_fields') and self.tournament.pref('team_name_generator') != 'user':
            self.instance.use_institution_prefix = bool(self.institution)

        if not self.cleaned_data.get('emoji', None):
            self.instance.emoji = pick_unused_emoji(tournament_id=self.tournament.id)[0]

        obj = super().save()
        self.save_answers(obj)

        obj.break_categories.set(self.tournament.breakcategory_set.filter(is_general=True))
        if obj.institution:
            obj.teaminstitutionconflict_set.create(institution=obj.institution)
        return obj


class SpeakerForm(CustomQuestionsFormMixin, forms.ModelForm):

    key = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, team, key, *args, tournament=None, **kwargs):
        self.team = team
        self.tournament = team.tournament
        super().__init__(*args, **kwargs)

        self.fields['key'].initial = key

        if not (self.tournament.pref('team_name_generator') == 'initials' or self.tournament.pref('code_name_generator') == 'last_names'):
            self.fields.pop('last_name')

        for field in ({'email', 'phone', 'gender', 'categories'} - set(self.tournament.pref('reg_speaker_fields'))):
            self.fields.pop(field)

        if 'categories' in self.fields:
            self.fields['categories'].queryset = self.tournament.speakercategory_set.filter(public=True)

        self.add_question_fields()

    class Meta:
        model = Speaker
        fields = ('name', 'last_name', 'email', 'phone', 'gender', 'categories')
        labels = {
            'name': _("Full name for tab"),
        }

    def save(self, commit=True):
        self.instance.team = self.team
        obj = super().save()
        populate_url_keys([obj])
        self.save_answers(obj)
        return obj


class AdjudicatorForm(CustomQuestionsFormMixin, forms.ModelForm):

    key = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, tournament, *args, institution=None, key=None, **kwargs):
        self.tournament = tournament
        self.institution = institution
        super().__init__(*args, **kwargs)

        if key:
            self.fields['key'].initial = key

        for field in ({'email', 'phone', 'gender'} - set(self.tournament.pref('reg_adjudicator_fields'))):
            self.fields.pop(field)

        if self.institution is not None:
            self.fields['institution'].widget = forms.HiddenInput()
            self.fields['institution'].initial = self.institution

        self.add_question_fields()

    class Meta:
        model = Adjudicator
        fields = ('name', 'institution', 'email', 'phone', 'gender')
        labels = {
            'name': _("Full name for tab"),
        }

    def save(self):
        self.instance.tournament = self.tournament
        if self.institution:
            self.instance.institution = self.institution

        obj = super().save()
        populate_url_keys([obj])
        self.save_answers(obj)

        if obj.institution:
            obj.adjudicatorinstitutionconflict_set.create(institution=obj.institution)
        return obj


class ParticipantAllocationForm(forms.Form):
    """Updates the number of participants allocated for each institution"""

    def __init__(self, tournament, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = tournament
        self._create_and_initialise_fields()

    @staticmethod
    def _fieldname_teams_allocated(institution):
        return 'teams_alloc_%(institution)d' % {'institution': institution.id}

    @staticmethod
    def _fieldname_adjs_allocated(institution):
        return 'adjs_alloc_%(institution)d' % {'institution': institution.id}

    def get_teams_allocated_field(self, institution):
        return self[self._fieldname_teams_allocated(institution)].as_widget(attrs={'class': 'form-control'})

    def get_adjs_allocated_field(self, institution):
        return self[self._fieldname_adjs_allocated(institution)].as_widget(attrs={'class': 'form-control'})

    def _create_and_initialise_fields(self):
        for t_inst in self.tournament.tournamentinstitution_set.select_related('institution').all():
            institution = t_inst.institution
            self.fields[self._fieldname_teams_allocated(institution)] = forms.IntegerField(min_value=0, required=False)
            self.initial[self._fieldname_teams_allocated(institution)] = t_inst.teams_allocated
            self.fields[self._fieldname_adjs_allocated(institution)] = forms.IntegerField(min_value=0, required=False)
            self.initial[self._fieldname_adjs_allocated(institution)] = t_inst.adjudicators_allocated

    def save(self):
        qs = self.tournament.tournamentinstitution_set.select_related('institution').all()

        items = self.tournament.priceitem_set.filter(active=True, item_type__in=[
            PriceItem.ItemType.PARTICIPANT, PriceItem.ItemType.TEAM, PriceItem.ItemType.SPEAKER,
            PriceItem.ItemType.ADJUDICATOR, PriceItem.ItemType.MISSING_ADJ,
        ])
        new_cart_items = []
        for t_inst in qs:
            institution = t_inst.institution

            if self.tournament.pref('inst_billing_standard') == 'allocated':
                n_adjs = self.cleaned_data[self._fieldname_adjs_allocated(institution)] - t_inst.adjudicators_allocated
                n_teams = self.cleaned_data[self._fieldname_teams_allocated(institution)] - t_inst.teams_allocated

                missing_adj_rule = MissingAdjudicatorRule.functions[self.tournament.pref('missing_adj_rule')]
                before_missing = max(missing_adj_rule(t_inst.adjudicators_allocated, t_inst.teams_allocated), 0)
                after_missing = missing_adj_rule(self.cleaned_data[self._fieldname_adjs_allocated(institution)], self.cleaned_data[self._fieldname_teams_allocated(institution)])
                new_missing = max(after_missing - before_missing, 0)

                cart_items = [
                    ci for ci in
                    [
                        add_item(items, PriceItem.ItemType.ADJUDICATOR, n_adjs),
                        add_item(items, PriceItem.ItemType.TEAM, n_teams),
                        add_item(items, PriceItem.ItemType.SPEAKER, n_teams * self.tournament.pref('speakers_in_team')),
                        add_item(items, PriceItem.ItemType.PARTICIPANT, n_adjs + n_teams * self.tournament.pref('speakers_in_team')),
                        add_item(items, PriceItem.ItemType.MISSING_ADJ, new_missing),
                    ]
                    if ci is not None and ci.quantity
                ]
                for ci in cart_items:
                    ci.institution = institution
                new_cart_items.extend(cart_items)

            t_inst.teams_allocated = self.cleaned_data[self._fieldname_teams_allocated(institution)]
            t_inst.adjudicators_allocated = self.cleaned_data[self._fieldname_adjs_allocated(institution)]
        TournamentInstitution.objects.bulk_update(qs, ['teams_allocated', 'adjudicators_allocated'])
        LineItem.objects.bulk_create(new_cart_items)


class PriceItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['item_type'].disabled = True


class CreatePaymentForm(forms.Form):
    def __init__(self, currency, max_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'] = forms.DecimalField(min_value=0, max_value=max_value, decimal_places=int(log10(currency.minor_unit)))


class FinishPayPalIntegrationForm(forms.Form):
    tracking_id = forms.CharField(widget=forms.HiddenInput(), required=True)
    merchant_id = forms.CharField(widget=forms.HiddenInput(), required=True)


class PayPalCaptureOrderForm(forms.Form):
    order_id = forms.CharField()
