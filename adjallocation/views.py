import json
from actionlog.models import ActionLogEntry
from draw.models import Debate
from participants.models import Adjudicator, Team

from .models import AdjudicatorConflict, AdjudicatorInstitutionConflict, AdjudicatorAdjudicatorConflict, DebateAdjudicator

from utils.views import *


@admin_required
@expect_post
@round_view
def create_adj_allocation(request, round):

    if round.draw_status == round.STATUS_RELEASED:
        return HttpResponseBadRequest("Draw is already released, unrelease draw to redo auto-allocations.")
    if round.draw_status != round.STATUS_CONFIRMED:
        return HttpResponseBadRequest("Draw is not confirmed, confirm draw to run auto-allocations.")

    from adjallocation.hungarian import HungarianAllocator
    round.allocate_adjudicators(HungarianAllocator)

    return _json_adj_allocation(round.get_draw(), round.unused_adjudicators())


@admin_required
@expect_post
@round_view
def update_debate_importance(request, round):
    id = int(request.POST.get('debate_id'))
    im = int(request.POST.get('value'))
    debate = Debate.objects.get(pk=id)
    debate.importance = im
    debate.save()
    ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_DEBATE_IMPORTANCE_EDIT,
                               user=request.user, debate=debate, tournament=round.tournament)
    return HttpResponse(im)


@admin_required
@round_view
def draw_adjudicators_edit(request, round):
    context = dict()
    context['draw'] = draw = round.get_draw()
    context['adj0'] = Adjudicator.objects.first()
    context['duplicate_adjs'] = round.tournament.pref('duplicate_adjs')
    context['feedback_headings'] = [
        q.name for q in round.tournament.adj_feedback_questions]

    def calculate_prior_adj_genders(team):
        debates = team.get_debates(round.seq)
        adjs = DebateAdjudicator.objects.filter(
            debate__in=debates).count()
        male_adjs = DebateAdjudicator.objects.filter(
            debate__in=debates, adjudicator__gender="M").count()
        if male_adjs > 0:
            male_adj_percent = int(male_adjs / adjs * 100)
            return male_adj_percent
        else:
            return 0

    for debate in draw:
        aff_male_adj_percent = calculate_prior_adj_genders(debate.aff_team)
        debate.aff_team.male_adj_percent = aff_male_adj_percent

        neg_male_adj_percent = calculate_prior_adj_genders(debate.neg_team)
        debate.neg_team.male_adj_percent = neg_male_adj_percent

        if neg_male_adj_percent > aff_male_adj_percent:
            debate.gender_class = (neg_male_adj_percent // 5) - 10
        else:
            debate.gender_class = (aff_male_adj_percent // 5) - 10

    regions = round.tournament.region_set.order_by('name')
    break_categories = round.tournament.breakcategory_set.order_by(
        'seq').exclude(is_general=True)
    colors = ["#C70062", "#00C79B", "#B1E001", "#476C5E",
              "#777", "#FF2983", "#6A268C", "#00C0CF", "#0051CF"]
    context['regions'] = list(zip(regions, colors + ["black"]
                             * (len(regions) - len(colors))))
    context['break_categories'] = list(zip(
        break_categories, colors + ["black"] * (len(break_categories) - len(colors))))

    return render(request, "draw_adjudicators_edit.html", context)


def _json_adj_allocation(debates, unused_adj):

    obj = {}

    def _adj(a):

        if a.institution.region:
            region_name = "region-%s" % a.institution.region.id
        else:
            region_name = ""

        return {
            'id': a.id,
            'name': a.name + " (" + a.institution.short_code + ")",
            'is_unaccredited': a.is_unaccredited,
            'gender': a.gender,
            'region': region_name
        }

    def _debate(d):
        r = {}
        if d.adjudicators.chair:
            r['chair'] = _adj(d.adjudicators.chair)
        r['panel'] = [_adj(a) for a in d.adjudicators.panel]
        r['trainees'] = [_adj(a) for a in d.adjudicators.trainees]
        return r

    obj['debates'] = dict((d.id, _debate(d)) for d in debates)
    obj['unused'] = [_adj(a) for a in unused_adj]

    return HttpResponse(json.dumps(obj))


@admin_required
@round_view
def draw_adjudicators_get(request, round):
    draw = round.get_draw()

    return _json_adj_allocation(draw, round.unused_adjudicators())


@admin_required
@round_view
def save_adjudicators(request, round):
    if request.method != "POST":
        return HttpResponseBadRequest("Expected POST")

    def id(s):
        s = s.replace('[]', '')
        return int(s.split('_')[1])

    debate_ids = set(id(a) for a in request.POST)
    debates = Debate.objects.in_bulk(list(debate_ids))
    debate_adjudicators = {}
    for d_id, debate in list(debates.items()):
        a = debate.adjudicators
        a.delete()
        debate_adjudicators[d_id] = a

    for key, vals in request.POST.lists():
        if key.startswith("chair_"):
            debate_adjudicators[id(key)].chair = vals[0]
        if key.startswith("panel_"):
            for val in vals:
                debate_adjudicators[id(key)].panel.append(val)
        if key.startswith("trainees_"):
            for val in vals:
                debate_adjudicators[id(key)].trainees.append(val)

    # We don't do any validity checking here, so that the adjudication
    # core can save a work in progress.

    for d_id, alloc in list(debate_adjudicators.items()):
        alloc.save()

    ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_ADJUDICATORS_SAVE,
                               user=request.user, round=round, tournament=round.tournament)

    return HttpResponse("ok")


@admin_required
@round_view
def adj_conflicts(request, round):

    data = {
        'personal': {},
        'history': {},
        'institutional': {},
        'adjudicator': {},
    }

    def add(type, adj_id, target_id):
        if adj_id not in data[type]:
            data[type][adj_id] = []
        data[type][adj_id].append(target_id)

    for ac in AdjudicatorConflict.objects.all():
        add('personal', ac.adjudicator_id, ac.team_id)

    for ic in AdjudicatorInstitutionConflict.objects.all():
        for team in Team.objects.filter(institution=ic.institution):
            add('institutional', ic.adjudicator_id, team.id)

    for ac in AdjudicatorAdjudicatorConflict.objects.all():
        add('adjudicator', ac.adjudicator_id, ac.conflict_adjudicator.id)

    history = DebateAdjudicator.objects.filter(
        debate__round__seq__lt=round.seq,
    )

    for da in history:
        add('history', da.adjudicator_id, da.debate.aff_team.id)
        add('history', da.adjudicator_id, da.debate.neg_team.id)

    return HttpResponse(json.dumps(data), content_type="text/json")
