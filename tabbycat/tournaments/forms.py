import math

from django.forms.fields import IntegerField
from django.forms import CharField, ChoiceField, ModelChoiceField, ModelForm
from django.utils.translation import gettext_lazy as _

from adjfeedback.models import AdjudicatorFeedbackQuestion
from breakqual.models import BreakCategory
from options.dynamic_preferences_registry import AdjCoreCredit, OrgComCredit, TabDirectorCredit
from options.presets import all_presets, get_preferences_data, presets_for_form, public_presets_for_form

from .models import Round, Tournament
from .utils import auto_make_break_rounds, auto_make_rounds


class TournamentStartForm(ModelForm):

    class Meta:
        model = Tournament
        fields = ('name', 'short_name', 'slug')

    num_prelim_rounds = IntegerField(
        min_value=1,
        label=_("Number of preliminary rounds"))

    break_size = IntegerField(
        min_value=2,
        required=False,
        label=_("Number of teams in the open break"),
        help_text=_("Leave blank if there are no break rounds."))

    def add_default_feedback_questions(self, tournament):
        agree = AdjudicatorFeedbackQuestion(
            tournament=tournament, seq=2, required=True,
            text="Did you agree with their decision?", name="Agree?",
            reference="agree", from_adj=True, from_team=True,
            answer_type=AdjudicatorFeedbackQuestion.ANSWER_TYPE_BOOLEAN_SELECT)
        agree.save()
        comments = AdjudicatorFeedbackQuestion(
            tournament=tournament, seq=3, required=False,
            text="Any further comments?", name="Comments?",
            reference="comments", from_adj=True, from_team=True,
            answer_type=AdjudicatorFeedbackQuestion.ANSWER_TYPE_LONGTEXT)
        comments.save()

    def save(self):
        tournament = super(TournamentStartForm, self).save()
        auto_make_rounds(tournament, self.cleaned_data["num_prelim_rounds"])

        break_size = self.cleaned_data["break_size"]
        if break_size:
            open_break = BreakCategory(
                tournament=tournament,
                # Translators: This is the name given to the 'Open Break'.
                name=_("Open"),
                slug="open",
                seq=1,
                break_size=break_size,
                is_general=True,
                priority=100
            )
            open_break.full_clean()
            open_break.save()

        self.add_default_feedback_questions(tournament)
        tournament.current_round = tournament.round_set.first()
        tournament.save()

        return tournament


class TournamentConfigureForm(ModelForm):

    class Meta:
        model = Tournament
        fields = ('preset_rules', 'public_info')

    preset_rules = ChoiceField(
        choices=presets_for_form(), # Tuple with (Present_Index, Preset_Name)
        label=_("Format Configuration"),
        help_text=_("Apply a standard set of settings to match a common debate format"))

    public_info = ChoiceField(
        choices=public_presets_for_form(), # Tuple with (Present_Index, Preset_Name)
        label=_("Public Configuration"),
        help_text=_("Show non-sensitive information on the public-facing side of this site, like draws (once released) and the motions of previous rounds"))

    tab_credit = CharField(
        label=TabDirectorCredit.verbose_name,
        required=False,
        help_text=TabDirectorCredit.help_text)

    org_credit = CharField(
        label=OrgComCredit.verbose_name,
        required=False,
        help_text=OrgComCredit.help_text)

    adj_credit = CharField(
        label=AdjCoreCredit.verbose_name,
        required=False,
        help_text=AdjCoreCredit.help_text)

    def save(self):
        presets = list(all_presets())
        t = self.instance

        # Identify + apply selected preset
        selected_index = self.cleaned_data["preset_rules"]
        selected_preset = next(p for p in presets if p.name == selected_index)
        selected_preferences = get_preferences_data(selected_preset, t)
        for preference in selected_preferences:
            t.preferences[preference['key']] = preference['new_value']

        # Apply public info presets
        do_public = self.cleaned_data["public_info"]
        public_preset = next((p for p in presets if p.name == do_public), False)
        if public_preset:
            public_preferences = get_preferences_data(public_preset, t)
            for preference in public_preferences:
                t.preferences[preference['key']] = preference['new_value']

        # Apply the credits
        t.preferences["public_features__tab_credit"] = self.cleaned_data["tab_credit"]
        t.preferences["public_features__org_credit"] = self.cleaned_data["org_credit"]
        t.preferences["public_features__adj_credit"] = self.cleaned_data["adj_credit"]

        # Create break rounds (need to do so after we know teams-per-room)
        open_break = BreakCategory.objects.filter(tournament=t, is_general=True).first()
        # Check there aren't already break rounds (i.e. when importing demos)
        existing_break_rounds_count = t.break_rounds().count()
        if open_break and existing_break_rounds_count == 0:
            if t.pref('teams_in_debate') == 'bp':
                num_break_rounds = math.ceil(math.log2(open_break.break_size / 2))
            else:
                num_break_rounds = math.ceil(math.log2(open_break.break_size))
            auto_make_break_rounds(t, num_break_rounds, open_break)


class CurrentRoundField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class SetCurrentRoundForm(ModelForm):

    current_round = CurrentRoundField(queryset=Round.objects.none(),
            required=True, empty_label=None)

    class Meta:
        model = Tournament
        fields = ('current_round',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_round'].queryset = self.instance.round_set.all()
