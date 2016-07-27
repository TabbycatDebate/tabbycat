from django.shortcuts import render
from django.db.models import Q
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from django.forms.widgets import CheckboxSelectMultiple
from django.forms.models import ModelMultipleChoiceField
from django.views.generic.base import TemplateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from divisions.models import Division
from tournaments.mixins import PublicTournamentPageMixin, RoundMixin
from utils.misc import redirect_round, reverse_round
from utils.mixins import ModelFormSetView, PostOnlyRedirectView, SuperuserRequiredMixin
from utils.views import admin_required, expect_post, round_view

from .models import Motion


class PublicMotionsView(PublicTournamentPageMixin, TemplateView):
    public_page_preference = 'public_motions_order'
    template_name = 'public_motions.html'

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        order_by = 'seq' if tournament.pref('public_motions_order') == 'forward' else '-seq'
        # Include rounds whether *either* motions are released *or* it's this
        # round or a previous round. The template checks motion_released again
        # and displays a "not released" message if motions are not released.
        kwargs['rounds'] = tournament.round_set.filter(
            Q(motions_released=True) | Q(seq__lte=tournament.current_round.seq)
        ).order_by(order_by).prefetch_related('motion_set')
        return super().get_context_data(**kwargs)


class EditMotionsView(SuperuserRequiredMixin, LogActionMixin, RoundMixin, ModelFormSetView):
    # Django doesn't have a class-based view for formsets, so this implements
    # the form processing analogously to FormView, with less decomposition.
    # See also: participants.views.PublicConfirmShiftView.

    template_name = 'edit.html'
    action_log_type = ActionLogEntry.ACTION_TYPE_MOTION_EDIT
    formset_factory_kwargs = dict(can_delete=True, extra=3, exclude=['round'])
    formset_model = Motion

    def get_formset_queryset(self):
        return self.get_round().motion_set.all()

    def formset_valid(self, formset):
        motions = formset.save(commit=False)
        round = self.get_round()
        for motion in motions:
            motion.round = round
            motion.save()
            self.log_action(motion=motion)
        for motion in formset.deleted_objects:
            motion.delete()
        return redirect_round('draw', self.get_round())


@admin_required
@round_view
def motions_assign(request, round):

    class MyModelChoiceField(ModelMultipleChoiceField):
        def label_from_instance(self, obj):
            return "D%s @ %s" % (
                obj.name,
                obj.venue_group.short_name,
            )

    class ModelAssignForm(ModelForm):
        divisions = MyModelChoiceField(
            widget=CheckboxSelectMultiple,
            queryset=Division.objects.filter(tournament=round.tournament).order_by('venue_group'))

        class Meta:
            model = Motion
            fields = ("divisions",)

    motion_form_set = modelformset_factory(Motion, ModelAssignForm, extra=0, fields=['divisions'])

    if request.method == 'POST':
        formset = motion_form_set(request.POST)
        formset.save()  # Should be checking for validity but on a deadline and was buggy
        if 'submit' in request.POST:
            return redirect_round('draw', round)

    formset = motion_form_set(queryset=Motion.objects.filter(round=round))
    return render(request, "assign.html", dict(formset=formset))


class BaseReleaseMotionsView(SuperuserRequiredMixin, LogActionMixin, RoundMixin, PostOnlyRedirectView):

    def get_redirect_url(self):
        return reverse_round('draw', self.get_round())

    def post(self, request, *args, **kwargs):
        round = self.get_round()
        round.motions_released = self.motions_released
        round.save()
        self.log_action()
        return super().post(request, *args, **kwargs)


class ReleaseMotionsView(BaseReleaseMotionsView):

    action_log_type = ActionLogEntry.ACTION_TYPE_MOTIONS_RELEASE
    motions_released = True


class UnreleaseMotionsView(BaseReleaseMotionsView):

    action_log_type = ActionLogEntry.ACTION_TYPE_MOTIONS_UNRELEASE
    motions_released = False


class DisplayMotionsView(SuperuserRequiredMixin, RoundMixin, TemplateView):

    template_name = 'show.html'

    def get_context_data(self, **kwargs):
        kwargs['motions'] = self.get_round().motion_set.all()
        return super().get_context_data(**kwargs)
