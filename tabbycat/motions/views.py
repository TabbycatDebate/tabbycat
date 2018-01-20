from django.contrib import messages
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.views.generic.base import TemplateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from tournaments.mixins import (CurrentRoundMixin, OptionalAssistantTournamentPageMixin,
                                PublicTournamentPageMixin, RoundMixin)
from utils.misc import redirect_round
from utils.mixins import AdministratorMixin
from utils.views import ModelFormSetView, PostOnlyRedirectView

from .models import Motion
from .forms import ModelAssignForm


class PublicMotionsView(PublicTournamentPageMixin, TemplateView):
    public_page_preference = 'public_motions'

    def using_division_motions(self):
        tournament = self.get_tournament()
        return tournament.pref('enable_divisions') and tournament.pref('enable_division_motions')

    def get_template_names(self):
        if self.using_division_motions():
            return ['public_division_motions.html']
        else:
            return ['public_motions.html']

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        order_by = 'seq' if tournament.pref('public_motions_order') == 'forward' else '-seq'

        # Include rounds whether *either* motions are released *or* it's this
        # round or a previous round. The template checks motion_released again
        # and displays a "not released" message if motions are not released.
        filter_q = Q(motions_released=True)
        if not self.using_division_motions():
            filter_q |= Q(seq__lte=tournament.current_round.seq)

        kwargs['rounds'] = tournament.round_set.filter(filter_q).order_by(
                order_by).prefetch_related('motion_set')
        return super().get_context_data(**kwargs)


class EditMotionsView(AdministratorMixin, LogActionMixin, RoundMixin, ModelFormSetView):
    # Django doesn't have a class-based view for formsets, so this implements
    # the form processing analogously to FormView, with less decomposition.
    # See also: participants.views.PublicConfirmShiftView.

    template_name = 'motions_edit.html'
    action_log_type = ActionLogEntry.ACTION_TYPE_MOTION_EDIT
    formset_model = Motion

    def get_formset_factory_kwargs(self):
        tournament = self.get_tournament()
        excludes = ['round', 'id']

        if not tournament.pref('enable_flagged_motions'):
            excludes.append('flagged')

        if not tournament.pref('enable_divisions'):
            excludes.append('divisions')

        nexisting = self.get_formset_queryset().count()
        if tournament.pref('enable_motions'):
            delete = True
            extras = max(3 - nexisting, 0)
        else:
            excludes.append('seq')
            extras = max(1 - nexisting, 0)
            delete = nexisting > 1  # if there's more than one, allow deletion

        return dict(can_delete=delete, extra=extras, exclude=excludes)

    def get_formset_queryset(self):
        return self.get_round().motion_set.all()

    def formset_valid(self, formset):
        motions = formset.save(commit=False)
        round = self.get_round()
        for i, motion in enumerate(motions, start=1):
            if not self.get_tournament().pref('enable_motions'):
                motion.seq = i
            motion.round = round
            motion.save()
            self.log_action(content_object=motion)
        for motion in formset.deleted_objects:
            motion.delete()

        count = len(motions)
        if not self.get_tournament().pref('enable_motions') and count == 1:
            messages.success(self.request, _("The motion has been saved."))
        elif count > 0:
            messages.success(self.request, ungettext("%(count)d motion has been saved.",
                "%(count)d motions have been saved.", count) % {'count': count})

        count = len(formset.deleted_objects)
        if count > 0:
            messages.success(self.request, ungettext("%(count)d motion has been deleted.",
                "%(count)d motions have been deleted.", count) % {'count': count})

        return redirect_round('draw-display', round)


class AssignMotionsView(AdministratorMixin, RoundMixin, ModelFormSetView):

    template_name = 'assign.html'
    formset_factory_kwargs = dict(extra=0, fields=['divisions'])
    formset_model = Motion

    def get_formset_queryset(self):
        return self.get_round().motion_set.all()

    def get_formset_class(self):
        return modelformset_factory(Motion, ModelAssignForm, extra=0, fields=['divisions'])

    def formset_valid(self, formset):
        formset.save()  # Should be checking for validity but on a deadline and was buggy
        messages.success(self.request, 'Those motion assignments have been saved.')
        return redirect_round('motions-edit', self.get_round())


class BaseReleaseMotionsView(AdministratorMixin, LogActionMixin, RoundMixin, PostOnlyRedirectView):

    round_redirect_pattern_name = 'draw-display'

    def post(self, request, *args, **kwargs):
        round = self.get_round()
        round.motions_released = self.motions_released
        round.save()
        self.log_action()
        messages.success(request, self.message_text)
        return super().post(request, *args, **kwargs)


class ReleaseMotionsView(BaseReleaseMotionsView):

    action_log_type = ActionLogEntry.ACTION_TYPE_MOTIONS_RELEASE
    motions_released = True
    message_text = _("Released the motion(s).")


class UnreleaseMotionsView(BaseReleaseMotionsView):

    action_log_type = ActionLogEntry.ACTION_TYPE_MOTIONS_UNRELEASE
    motions_released = False
    message_text = _("Unreleased the motion(s).")


class BaseDisplayMotionsView(RoundMixin, TemplateView):

    template_name = 'show.html'

    def get_context_data(self, **kwargs):
        kwargs['motions'] = self.get_round().motion_set.all()
        kwargs['infos'] = self.get_round().motion_set.exclude(info_slide="")
        return super().get_context_data(**kwargs)


class AdminDisplayMotionsView(AdministratorMixin, BaseDisplayMotionsView):
    pass


class AssistantDisplayMotionsView(CurrentRoundMixin, OptionalAssistantTournamentPageMixin, BaseDisplayMotionsView):
    assistant_page_permissions = ['all_areas']
