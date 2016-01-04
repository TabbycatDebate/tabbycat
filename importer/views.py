from utils.views import *

from . import forms

from participants.models import Adjudicator, Institution, Team, Speaker
from venues.models import Venue

@admin_required
@tournament_view
def data_index(request, t):
    return r2r(request, 'data_index.html')

# INSTITUTIONS

@admin_required
@tournament_view
def add_institutions(request, t):
    print("adding insts")
    #form = forms.AddInstitutionsForm
    return r2r(request, 'add_institutions.html')

@admin_required
@expect_post
@tournament_view
def edit_institutions(request, t):
    institutions = []
    institution_lines = request.POST['institutions_raw'].split('\n')
    for line in institution_lines:
        try:
            full_name = line.split(',')[0].strip()
            short_name = line.split(',')[1].strip()
            institution = Institution(name=full_name, code=short_name)
            institutions.append(institution)
        except:
            pass # TODO

    return r2r(request, 'edit_institutions.html', dict(institutions=institutions))


@admin_required
@expect_post
@tournament_view
def confirm_institutions(request, t):
    institution_names = request.POST.getlist('institution_names')
    institution_codes = request.POST.getlist('institution_codes')

    for i, key in enumerate(institution_names):
        try:
            full_name = institution_names[i]
            short_name = institution_codes[i]
            institution = Institution(name=full_name, code=short_name)
            institution.save()
        except:
            pass

    confirmed = {"kind": "Institutions", "quantity": len(institution_names) }
    return r2r(request, 'confirmed_data.html', dict(confirmed=confirmed))

# VENUES

@admin_required
@tournament_view
def add_venues(request, t):
    form = forms.AddVenuesForm
    return r2r(request, 'add_venues.html')

@admin_required
@expect_post
@tournament_view
def edit_venues(request, t):
    venues = {}
    venue_lines = request.POST['venues_raw'].split('\n')
    for line in venue_lines:
        try:
            name = line.split(',')[0].strip()
            priority = line.split(',')[1].strip()
            venues[name] = priority
        except:
            pass # TODO

    return r2r(request, 'edit_venues.html', dict(venues=venues))

@admin_required
@expect_post
@tournament_view
def confirm_venues(request, t):
    venue_names = request.POST.getlist('venue_names')
    venue_priorities = request.POST.getlist('venue_priorities')
    for i, key in enumerate(venue_names):
        try:
            venue = Venue(name=venue_names[i], priority=venue_priorities[i])
            venue.save()
        except:
            pass

    confirmed = {"kind": "Venues", "quantity": len(venue_names) }
    return r2r(request, 'confirmed_data.html', dict(confirmed=confirmed))

# TEAMS

@admin_required
@tournament_view
def add_teams(request, t):
    institutions = Institution.objects.all()
    form = forms.AddTeamsForm
    return r2r(request, 'add_teams.html', dict(institutions=institutions))


@admin_required
@expect_post
@tournament_view
def edit_teams(request, t):
    institutions = {}
    for name, quantity in request.POST.items():
        if quantity:
            institutions[name] = list(range(1, int(quantity) + 1)) # Create a placeholder for loop

    return r2r(request, 'edit_teams.html', dict(institutions=institutions))


@admin_required
@expect_post
@tournament_view
def confirm_teams(request, t):
    sorted_post = sorted(request.POST.items())

    for i in range(0, len(sorted_post) - 1, 4): # Sort through the items advancing 4 at a time
        instititution_name = sorted_post[i][1]
        team_name = sorted_post[i+1][1]
        use_prefix = False
        if (sorted_post[i+2][1] == "on"):
            use_prefix = True
        use_prefix = sorted_post[i+2][1]
        speaker_names = sorted_post[i+3][1].split(',')

        institution = Institution.objects.get(name=instititution_name)
        if team_name and speaker_names and institution:
            newteam = Team(
                institution = institution,
                reference = team_name,
                short_reference = team_name[:34],
                tournament=t,
                use_institution_prefix = use_prefix,
            )
            newteam.save()
            for speaker in speaker_names:
                newspeaker = Speaker(
                    name = speaker,
                    team = newteam
                )
                newspeaker.save()

    confirmed = {"kind": "Teams", "quantity": int((len(sorted_post) - 1) / 4) }
    return r2r(request, 'confirmed_data.html', dict(confirmed=confirmed))

# ADJUDICATORS

@admin_required
@tournament_view
def add_adjudicators(request, t):
    institutions = Institution.objects.all()
    form = forms.AddAdjudicatorsForm
    return r2r(request, 'add_adjudicators.html', dict(institutions=institutions))


@admin_required
@expect_post
@tournament_view
def edit_adjudicators(request, t):
    institutions = {}
    for name, quantity in request.POST.items():
        if quantity:
            institutions[name] = list(range(1, int(quantity) + 1)) # Create a placeholder for loop

    context = {
        'institutions'      : institutions,
        'score_min'         : t.config.get('adj_min_score'),
        'score_max'         : t.config.get('adj_max_score'),
        'score_avg'         : round((t.config.get('adj_max_score') + t.config.get('adj_min_score')) / 2, 1),
    }
    return r2r(request, 'edit_adjudicators.html', context)

@admin_required
@expect_post
@tournament_view
def confirm_adjudicators(request, t):
    sorted_post = sorted(request.POST.items())

    for i in range(0, len(sorted_post) - 1, 3): # Sort through the items advancing 3 at a time
        institution_name = sorted_post[i][1]
        adj_name = sorted_post[i+1][1]
        adj_rating = sorted_post[i+2][1]

        institution = Institution.objects.get(name=institution_name)
        if adj_name and adj_rating and institution:
            newadj = Adjudicator(
                institution = institution,
                name = adj_name,
                tournament = t,
                test_score = adj_rating,
            )
            newadj.save()

    confirmed = {"kind": "Adjudicators", "quantity": int((len(sorted_post) - 1) / 3) }
    return r2r(request, 'confirmed_data.html', dict(confirmed=confirmed))
