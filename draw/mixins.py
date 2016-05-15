import json
from collections import OrderedDict
from django.views.generic.base import TemplateView
from tournaments.mixins import RoundMixin

class DrawTablePage(RoundMixin, TemplateView):

    template_name = 'draw_display_by.html'

    def create_row(self, d, t, sort_key=None, sort_value=None):
        ddict = []
        if sort_key and sort_value:
            ddict.append((sort_key, sort_value))
        if t.pref('enable_divisions'):
            ddict.append(('division', d.division.name))
        if t.pref('enable_venue_groups'):
            if d.division:
                ddict.append(('venue', d.division.venue_group.short_name ))
            else:
                ddict.append(('venue', d.venue.group.short_name + d.venue.name))
        else:
            ddict.append(('venue', d.venue.name ))
        if t.pref('enable_debate_scheduling'):
            if d.aff_team.type == 'B' or d.neg_team.type == 'B':
                ddict.append((' ', "" ))
                ddict.append((' ', "Bye" ))
            elif d.result_status == "P" :
                ddict.append((' ', "" ))
                ddict.append((' ', "Postponed" ))
            elif d.confirmed_ballot.forfeit :
                ddict.append((' ', "" ))
                ddict.append((' ', "Forfeit" ))
            else:
                ddict.append(('status', d.time.strftime("D jS F" )))
                ddict.append(('status', d.time.strftime('h:i A' )))
        ddict.append(('aff', d.aff_team.short_name))
        if t.pref('show_emoji'):
            ddict.append(('AE', d.aff_team.emoji))
        ddict.append(('neg', d.neg_team.short_name))
        if t.pref('show_emoji'):
            ddict.append(('NE', d.neg_team.emoji))
        if t.pref('enable_division_motions'):
            ddict.append(('Motion', [m.reference for m in d.division_motions]))
        if not t.pref('enable_divisions'):
            ddict.append(('adjudicators', d.adjudicators_for_draw ))

        return OrderedDict(ddict)

    def get_context_data(self, **kwargs):
        round = self.get_round()
        draw = round.get_draw()
        t = self.get_tournament()
        if self.sorting is "team":
            draw_data = []
            for d in draw:
                aff_row = self.create_row(d, t, 'Team', d.aff_team.short_name)
                neg_row = self.create_row(d, t, 'Team', d.neg_team.short_name)
                draw_data.extend([aff_row, neg_row])
        else:
            draw_data = [self.create_row(debate, t) for debate in draw]

        kwargs["tableData"] = json.dumps(draw_data)
        kwargs["round"] = self.get_round()
        return super().get_context_data(**kwargs)