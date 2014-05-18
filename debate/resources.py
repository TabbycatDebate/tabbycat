from import_export import resources, fields
from debate.models import Tournament, Venue, Institution, Speaker, Adjudicator, Round

class TournamentResource(resources.ModelResource):
    class Meta:
        model = Tournament

class VenueResource(resources.ModelResource):
    class Meta:
        model = Venue


class InstitutionResource(resources.ModelResource):
    class Meta:
        model = Institution


class SpeakerResource(resources.ModelResource):
    class Meta:
        model = Speaker


class AdjudicatorResource(resources.ModelResource):
    instutition = fields.Field()

    class Meta:
        model = Adjudicator
        exclude = ('barcode_id','checkin_message','conflicts','institution','institution_conflicts')

    def dehydrate_instutition(self, adj):
        return "%s" % (adj.institution)


class RoundResource(resources.ModelResource):
    class Meta:
        model = Round
        exclude = ('draw_status','venue_status','adjudicator_status','checkins','active_venues','active_adjudicators','active_teams',)