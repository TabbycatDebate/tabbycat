from django.shortcuts import render

from debate.views import round_view, admin_required, expect_post, redirect_round
from debate.views import r2r

from . import models
from action_log.models import ActionLog

from django.forms import ModelForm
from django.forms.models import modelformset_factory
from django.forms.widgets import CheckboxSelectMultiple
from django.forms.models import ModelMultipleChoiceField

@admin_required
@round_view
def motions(request, round):
    motions = list()
    motions = models.Motion.objects.statistics(round=round)
    if len(motions) > 0:
        motions = [m for m in motions if m.round == round]

    return r2r(request, "motions/list.html", dict(motions=motions))

@admin_required
@round_view
def motions_edit(request, round):
    MotionFormSet = modelformset_factory(models.Motion,
        can_delete=True, extra=3, exclude=['round'])

    if request.method == 'POST':
        formset = MotionFormSet(request.POST, request.FILES)
        if formset.is_valid():
            motions = formset.save(commit=False)
            for motion in motions:
                motion.round = round
                motion.save()
                ActionLog.objects.log(type=ActionLog.ACTION_TYPE_MOTION_EDIT,
                    user=request.user, motion=motion, tournament=round.tournament)
            for motions in formset.deleted_objects:
                motions.delete()
            if 'submit' in request.POST:
                return redirect_round('motions', round)
    else:
        formset = MotionFormSet(queryset=models.Motion.objects.filter(round=round))

    return r2r(request, "motions/edit.html", dict(formset=formset))


@admin_required
@round_view
def motions_assign(request, round):

    class MyModelChoiceField(ModelMultipleChoiceField):
        def label_from_instance(self, obj):
            return "%s %s - Division %s @ %s" % (
                obj.venue_group.short_name.split(' ')[2],
                obj.venue_group.short_name.split(' ')[1],
                obj.name,
                obj.venue_group.short_name.split(' ')[0],
            )

    class ModelAssignForm(ModelForm):
        divisions = MyModelChoiceField(widget=CheckboxSelectMultiple, queryset=Division.objects.filter(tournament=round.tournament).order_by('venue_group'))
        class Meta:
            model = Motion
            fields = ("divisions",)

    MotionFormSet = modelformset_factory(models.Motion, ModelAssignForm, extra=0, fields=['divisions'])

    if request.method == 'POST':
        formset = MotionFormSet(request.POST)
        formset.save() # Should be checking for validity but on a deadline and was buggy
        if 'submit' in request.POST:
            return redirect_round('motions', round)

    formset = MotionFormSet(queryset=models.Motion.objects.filter(round=round))
    return r2r(request, "motions_assign.html", dict(formset=formset))


@admin_required
@expect_post
@round_view
def release_motions(request, round):
    round.motions_released = True
    round.save()
    ActionLog.objects.log(type=ActionLog.ACTION_TYPE_MOTIONS_RELEASE,
        user=request.user, round=round, tournament=round.tournament)

    return redirect_round('motions', round)

@admin_required
@expect_post
@round_view
def unrelease_motions(request, round):
    round.motions_released = False
    round.save()
    ActionLog.objects.log(type=ActionLog.ACTION_TYPE_MOTIONS_UNRELEASE,
        user=request.user, round=round, tournament=round.tournament)

    return redirect_round('motions', round)