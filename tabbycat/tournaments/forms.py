from django.forms.fields import IntegerField
from django.forms import CharField, ChoiceField, ModelChoiceField, ModelForm
from django.utils.translation import gettext_lazy as _
from django_summernote.widgets import SummernoteWidget

from adjfeedback.models import AdjudicatorFeedbackQuestion
from breakqual.models import BreakCategory
from draw.generator.utils import ispow2
from options.preferences import TournamentStaff
from options.presets import all_presets, get_preferences_data, presets_for_form, public_presets_for_form

from .models import Round, Tournament
from .utils import auto_make_break_rounds, auto_make_rounds


class TournamentConfigureForm(ModelForm):

    class Meta:
        model = Tournament
        fields = ('preset_rules', 'public_info')

    preset_rules = ChoiceField(
        choices=[(None, "--------")] + presets_for_form(), # Tuple with (Present_Index, Preset_Name)
        label=_("Format Configuration"),
        help_text=_("Apply a standard set of settings to match a common debate format"),
        required=False)

    public_info = ChoiceField(
        choices=public_presets_for_form(), # Tuple with (Present_Index, Preset_Name)
        label=_("Public Configuration"),
        help_text=_("Show non-sensitive information on the public-facing side of this site, like draws (once released) and the motions of previous rounds"))

    num_prelim_rounds = IntegerField(
        min_value=1,
        label=_("Number of preliminary rounds"))

    break_size = IntegerField(
        min_value=2,
        required=False,
        label=_("Number of teams in the open break"),
        help_text=_("Leave blank if there are no break rounds."))

    tournament_staff = CharField(
        label=TournamentStaff.verbose_name,
        required=False,
        help_text=TournamentStaff.help_text,
        initial=_("<strong>Tabulation:</strong> [list tabulation staff here]<br />"
            "<strong>Organisation:</strong> [list organising committee members here]<br />"
            "<strong>Adjudication:</strong> [list chief adjudicators here]"),
        widget=SummernoteWidget(attrs={'height': 150}),
    )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('preset_rules') == 'British Parliamentary Rules':
            break_size = cleaned_data.get('break_size')
            if (break_size is not None and
                    not (break_size % 6 == 0 and ispow2(break_size // 6)) and
                    not (break_size % 4 == 0 and ispow2(break_size // 4))):
                self.add_error('break_size', _("In British Parliamentary tournaments, "
                    "the number of breaking teams must be either six times or four "
                    "times a power of two (4, 6, 8, 12, 16, 24, 32, 48, …)."))

    @staticmethod
    def add_default_feedback_questions(tournament):
        agree = AdjudicatorFeedbackQuestion(
            tournament=tournament, seq=2, required=True,
            text=_("Did you agree with their decision?"), name=_("Agree?"),
            reference="agree", from_adj=True, from_team=True,
            answer_type=AdjudicatorFeedbackQuestion.ANSWER_TYPE_BOOLEAN_SELECT)
        agree.save()
        comments = AdjudicatorFeedbackQuestion(
            tournament=tournament, seq=3, required=False,
            text=_("Comments"), name=_("Comments"),
            reference="comments", from_adj=True, from_team=True,
            answer_type=AdjudicatorFeedbackQuestion.ANSWER_TYPE_LONGTEXT)
        comments.save()

    def save(self):
        tournament = self.instance

        presets = list(all_presets())

        # Identify + apply selected preset
        selected_index = self.cleaned_data["preset_rules"]
        if selected_index:
            selected_preset = next(p for p in presets if p.name == selected_index)
            selected_preferences = get_preferences_data(selected_preset, tournament)
            for preference in selected_preferences:
                tournament.preferences[preference['key']] = preference['new_value']

        # Apply public info presets
        do_public = self.cleaned_data["public_info"]
        public_preset = next((p for p in presets if p.name == do_public), False)
        if public_preset:
            public_preferences = get_preferences_data(public_preset, tournament)
            for preference in public_preferences:
                tournament.preferences[preference['key']] = preference['new_value']

        if not tournament.round_set.exists():
            auto_make_rounds(tournament, self.cleaned_data["num_prelim_rounds"])

        if not tournament.adjudicatorfeedbackquestion_set.exists():
            self.add_default_feedback_questions(tournament)

        tournament.current_round = tournament.round_set.order_by('seq').first()
        tournament.save()

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

            if tournament.preferences['debate_rules__teams_in_debate'] == 'bp':
                num_break_rounds = ((break_size - 1) // 2).bit_length()
            else:
                num_break_rounds = (break_size - 1).bit_length()
            auto_make_break_rounds(tournament, num_break_rounds, open_break)

        # Apply the credits
        if self.cleaned_data['tournament_staff'] != self.fields['tournament_staff'].initial:
            tournament.preferences["public_features__tournament_staff"] = self.cleaned_data["tournament_staff"]

        return tournament


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
