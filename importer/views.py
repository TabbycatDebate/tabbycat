from utils.views import *

from . import forms

from participants.models import Adjudicator, Institution, Team, Speaker
from venues.models import Venue, VenueGroup, InstitutionVenueConstraint


@admin_required
@tournament_view
def data_index(request, t):
    return render(request, 'data_index.html')


# INSTITUTIONS

@admin_required
@tournament_view
def add_institutions(request, t):
    form = forms.AddInstitutionsForm
    return render(request, 'add_institutions.html')


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
            pass  # TODO

    return render(request,
                  'edit_institutions.html',
                  dict(institutions=institutions))


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

    confirmed = {"kind": "Institutions", "quantity": len(institution_names)}
    return render(request, 'confirmed_data.html', dict(confirmed=confirmed))

# VENUES

@admin_required
@tournament_view
def add_venues(request, t):
    form = forms.AddVenuesForm
    return render(request, 'add_venues.html')

@admin_required
@expect_post
@tournament_view
def edit_venues(request, t):
    venues = []
    venue_lines = request.POST['venues_raw'].split('\n')
    for line in venue_lines:
        try:
            name = line.split(',')[0].strip()
            priority = line.split(',')[1].strip()
            if len(line.split(',')) > 2:
                venues.append({
                    'name': name,
                    'priority': priority,
                    'group': line.split(',')[2].strip()
                })
            else:
                venues.append({'name': name, 'priority': priority, })
        except:
            pass  # TODO

    return render(request, 'edit_venues.html', dict(venues=venues))


@admin_required
@expect_post
@tournament_view
def confirm_venues(request, t):
    print(request.POST)
    venue_names = request.POST.getlist('venue_names')
    venue_priorities = request.POST.getlist('venue_priorities')
    venue_groups = request.POST.getlist('venue_groups')
    venue_shares = request.POST.getlist('venue_shares')
    for i, key in enumerate(venue_names):
        if venue_groups[i]:
            try:
                venue_group = VenueGroup.objects.get(short_name=venue_groups[i])
            except VenueGroup.DoesNotExist:
                try:
                    venue_group = VenueGroup.objects.get(name=venue_groups[i])
                except VenueGroup.DoesNotExist:
                    venue_group = VenueGroup(name=venue_groups[i],
                        short_name=venue_groups[i][:15]).save()
        else:
            venue_group = None

        if venue_shares[i] == "yes":
            venue_tournament = None
        else:
            venue_tournament = t

        venue = Venue(name=venue_names[i], priority=venue_priorities[i],
                      group=venue_group, tournament=venue_tournament)
        venue.save()

    confirmed = {"kind": "Venues", "quantity": len(venue_names)}
    return render(request, 'confirmed_data.html', dict(confirmed=confirmed))

# VENUE PREFERENCES

@admin_required
@tournament_view
def add_venue_preferences(request, t):
    institutions = Institution.objects.all()
    return render(request,
                  'add_venue_preferences.html',
                  dict(institutions=institutions))


@admin_required
@expect_post
@tournament_view
def edit_venue_preferences(request, t):

    venue_groups = VenueGroup.objects.all()
    institutions = []

    for institution_id, checked in request.POST.items():
        institutions.append(Institution.objects.get(pk=institution_id))

    return render(request,
                  'edit_venue_preferences.html',
                  dict(institutions=institutions,
                       venue_groups=venue_groups))


@admin_required
@expect_post
@tournament_view
def confirm_venue_preferences(request, t):

    institutions = []
    for institution_id in request.POST.getlist('institutionIDs'):
        institution = Institution.objects.get(pk=institution_id)
        InstitutionVenueConstraint.objects.filter(
            institution=institution).delete()

    venue_priorities = request.POST.dict()
    del venue_priorities["institutionIDs"]

    created_preferences = 0

    for idset, priority in venue_priorities.items():
        institution_id = idset.split('_')[0]
        venue_group_id = idset.split('_')[1]

        if institution_id and venue_group_id and priority:
            # print('making a pref')
            institution = Institution.objects.get(pk=int(institution_id))
            venue_group = VenueGroup.objects.get(pk=int(venue_group_id))
            venue_preference = InstitutionVenueConstraint(
                institution=institution,
                priority=priority,
                venue_group=venue_group)
            venue_preference.save()
            created_preferences += 1

    confirmed = {"kind": "Venue Preferences", "quantity": created_preferences}
    return render(request, 'confirmed_data.html', dict(confirmed=confirmed))

# TEAMS


@admin_required
@tournament_view
def add_teams(request, t):
    institutions = Institution.objects.all()
    form = forms.AddTeamsForm
    return render(request, 'add_teams.html', dict(institutions=institutions))


@admin_required
@expect_post
@tournament_view
def edit_teams(request, t):
    institutions_with_team_numbers = []

    # Set default speaker text to match tournament setup
    default_speakers = ""
    for i in range(1, t.pref('substantive_speakers') + 1):
        if i > 1: default_speakers += ","
        default_speakers += "Speaker %s" % i

    for name, quantity in request.POST.items():
        if quantity:
            desired_teams_count = int(quantity) + 1  # +1 as we dont want teams named 0
            institution = Institution.objects.get(name=name)
            team_names = Team.objects.filter(
                institution=institution,
                tournament=t).values_list('reference',
                                          flat=True).order_by('reference')
            available_team_numbers = []

            name_to_check = 1
            while name_to_check < desired_teams_count:
                # print('i is ', name_to_check)
                # Check if the team name/number already exists
                if str(name_to_check) in team_names:
                    # print('     team exists:', name_to_check)
                    desired_teams_count += 1
                else:
                    # print('     team doesnt exist:', name_to_check)
                    available_team_numbers.append(name_to_check)

                name_to_check += 1

            institutions_with_team_numbers.append({
                'name': institution.name,
                'id': institution.id,
                'available_team_numbers': available_team_numbers
            })
            # print('____')

    return render(request, 'edit_teams.html',
                  dict(institutions=institutions_with_team_numbers,
                       default_speakers=default_speakers))


@admin_required
@expect_post
@tournament_view
def confirm_teams(request, t):
    sorted_post = sorted(request.POST.items())

    for i in range(0, len(sorted_post) - 1,
                   4):  # Sort through the items advancing 4 at a time
        instititution_id = sorted_post[i][1]
        team_name = sorted_post[i + 1][1]
        use_prefix = False
        if (sorted_post[i + 2][1] == "yes"):
            use_prefix = True
        speaker_names = sorted_post[i + 3][1].split(',')

        institution = Institution.objects.get(id=instititution_id)
        if team_name and speaker_names and institution:
            newteam = Team(institution=institution,
                           reference=team_name,
                           short_reference=team_name[:34],
                           tournament=t,
                           use_institution_prefix=use_prefix, )
            newteam.save()
            for speaker in speaker_names:
                newspeaker = Speaker(name=speaker, team=newteam)
                newspeaker.save()

    confirmed = {"kind": "Teams", "quantity": int((len(sorted_post) - 1) / 4)}
    return render(request, 'confirmed_data.html', dict(confirmed=confirmed))

# ADJUDICATORS


@admin_required
@tournament_view
def add_adjudicators(request, t):
    institutions = Institution.objects.all()
    form = forms.AddAdjudicatorsForm
    return render(request,
                  'add_adjudicators.html',
                  dict(institutions=institutions))


@admin_required
@expect_post
@tournament_view
def edit_adjudicators(request, t):
    institutions = {}
    for name, quantity in request.POST.items():
        if quantity:
            # Create a placeholder for loop
            institutions[name] = list(range(1, int(quantity) + 1))

    context = {
        'institutions': institutions,
        'score_avg': round(
            (t.pref('adj_max_score') + t.pref('adj_min_score')) / 2, 1),
    }
    return render(request, 'edit_adjudicators.html', context)


@admin_required
@expect_post
@tournament_view
def confirm_adjudicators(request, t):
    sorted_post = sorted(request.POST.items())

    for i in range(0, len(sorted_post), 4):
        # Sort through the items advancing 4 at a time
        adj_institution = Institution.objects.get(name=sorted_post[i][1])
        adj_name = sorted_post[i + 1][1]
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

    confirmed = {"kind": "Adjudicators",
                 "quantity": int((len(sorted_post) - 1) / 3)}
    return render(request, 'confirmed_data.html', dict(confirmed=confirmed))
