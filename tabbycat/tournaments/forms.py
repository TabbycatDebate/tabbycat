from django.forms import CharField, ChoiceField, Form, ModelChoiceField, ModelForm
from django.forms.fields import IntegerField
from django.forms.models import ModelChoiceIterator
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_summernote.widgets import SummernoteWidget

from adjfeedback.models import AdjudicatorFeedbackQuestion
from breakqual.models import BreakCategory
from breakqual.utils import auto_make_break_rounds
from options.preferences import TournamentStaff
from options.presets import all_presets, get_preferences_data, presets_for_form, public_presets_for_form

from .models import Round, Tournament
from .utils import auto_make_rounds


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
                priority=100,
            )
            open_break.full_clean()
            open_break.save()

        self.add_default_feedback_questions(tournament)
        tournament.current_round = tournament.round_set.order_by('seq').first()
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

    tournament_staff = CharField(
        label=TournamentStaff.verbose_name,
        required=False,
        help_text=TournamentStaff.help_text,
        initial=_("<strong>Tabulation:</strong> [list tabulation staff here]<br />"
            "<strong>Organisation:</strong> [list organising committee members here]<br />"
            "<strong>Adjudication:</strong> [list chief adjudicators here]"),
        widget=SummernoteWidget(attrs={'height': 150, 'class': 'form-summernote'}),
    )

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
        if self.cleaned_data['tournament_staff'] != self.fields['tournament_staff'].initial:
            t.preferences["public_features__tournament_staff"] = self.cleaned_data["tournament_staff"]

        # Create break rounds (need to do so after we know teams-per-room)
        open_break = BreakCategory.objects.filter(tournament=t, is_general=True).first()
        # Check there aren't already break rounds (i.e. when importing demos)
        if open_break and not t.break_rounds().exists():
            auto_make_break_rounds(open_break, t, False)


class RoundWithCompleteOptionChoiceIterator(ModelChoiceIterator):

    def __iter__(self):
        yield from super().__iter__()
        yield (self.field.complete_value, self.field.complete_label)

    def __len__(self):
        return super().__len__() + 1

    def __bool__(self):
        return True  # the "complete" option always exists


class RoundField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class RoundWithCompleteOptionField(RoundField):

    iterator = RoundWithCompleteOptionChoiceIterator
    complete_value = "all-completed"

    def __init__(self, *args, complete_label="", **kwargs):
        self.complete_label = complete_label
        return super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value == self.complete_value:
            return self.complete_value
        return super().to_python(value)


class SetCurrentRoundSingleBreakCategoryForm(Form):
    """Form to set completed rounds in a tournament with a single break category."""

    current_round = RoundField(queryset=Round.objects.none(), required=True, empty_label=None)

    def __init__(self, tournament, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = tournament
        self.fields['current_round'].queryset = tournament.round_set.order_by('seq')
        self.fields['current_round'].initial = tournament.current_round

    def save(self):
        seq = self.cleaned_data['current_round'].seq
        self.tournament.round_set.filter(seq__lt=seq).update(completed=True)
        self.tournament.round_set.filter(seq__gte=seq).update(completed=False)


class SetCurrentRoundMultipleBreakCategoriesForm(Form):
    """Form to set completed rounds in a tournament with multiple break categories."""

    prelim = RoundWithCompleteOptionField(queryset=Round.objects.none(), required=True,
        label=_("Current preliminary round"),
        complete_label=_("All preliminary rounds have been completed"))

    def __init__(self, tournament, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = tournament
        self.fields['prelim'].queryset = tournament.prelim_rounds()
        current_prelim_round = tournament.prelim_rounds().filter(completed=False).order_by('seq').first()
        self.fields['prelim'].initial = current_prelim_round or RoundWithCompleteOptionField.complete_value

        for category in tournament.breakcategory_set.all():
            self.fields['elim_' + category.slug] = RoundWithCompleteOptionField(
                queryset=category.round_set.all(),
                label=mark_safe(_("Current elimination round in <strong>%(category)s</strong> "
                    "<em>(only if all preliminary rounds have been completed)</em>") % {
                    'category': escape(category.name)}),
                required=False,
                initial=((category.round_set.filter(completed=False).order_by('seq').first() or
                    RoundWithCompleteOptionField.complete_value) if current_prelim_round is None else None),
                complete_label=_("All elimination rounds in %(category)s have been completed") % {
                    'category': category.name},
            )

    def clean(self):
        cleaned_data = super().clean()

        elim_fields = ['elim_' + category.slug for category in self.tournament.breakcategory_set.all()]

        if cleaned_data.get('prelim') != RoundWithCompleteOptionField.complete_value:
            for field in elim_fields:
                if cleaned_data.get(field) is not None:
                    self.add_error(field, _("If the current round is a preliminary round, "
                        "this field must be blank."))

        else:
            for field in elim_fields:
                if cleaned_data.get(field) is None:
                    self.add_error(field, _("If all preliminary rounds have been completed, "
                        "this field is required."))

    def save(self):
        if self.cleaned_data['prelim'] != RoundWithCompleteOptionField.complete_value:
            seq = self.cleaned_data['prelim'].seq
            self.tournament.prelim_rounds().filter(seq__lt=seq).update(completed=True)
            self.tournament.prelim_rounds().filter(seq__gte=seq).update(completed=False)
            self.tournament.break_rounds().update(completed=False)

        else:
            self.tournament.prelim_rounds().update(completed=True)
            for category in self.tournament.breakcategory_set.all():
                value = self.cleaned_data['elim_' + category.slug]
                if value == RoundWithCompleteOptionField.complete_value:
                    category.round_set.update(completed=True)
                else:
                    seq = self.cleaned_data['elim_' + category.slug].seq
                    category.round_set.filter(seq__lt=seq).update(completed=True)
                    category.round_set.filter(seq__gte=seq).update(completed=False)
