from importer import BaseTournamentDataImporter, TournamentDataImporterError
import debate.models as m

class AnorakTournamentDataImporter(BaseTournamentDataImporter):
    """Anorak: The original tournament data format."""

    def import_rounds(self, f):
        """Imports rounds from a file.
        Each line has:
            seq, name, abbreviation, stage, draw_type, silent, feedback_weight
        """
        def _round_line_parser(line):
            return {
                'tournament'      : self.tournament,
                'seq'             : int(line[0]),
                'name'            : line[1],
                'abbreviation'    : line[2],
                'stage'           : self._lookup(self.ROUND_STAGES, line[3] or "p", "draw stage"),
                'draw_type'       : self._lookup(self.ROUND_DRAW_TYPES, line[4] or "r", "draw type"),
                'silent'          : bool(int(line[5])),
                'feedback_weight' : float(line[6]) or 0.7,
            }
        counts, errors = self._import(f, _round_line_parser, m.Round)

        # Set the round with the lowest known seqno to be the current round.
        # TODO (as above)
        self.tournament.current_round = m.Round.objects.get(
                tournament=self.tournament, seq=1)
        self.tournament.save()

        return counts, errors

    def import_institutions(self, f):
        """Imports institutions from a file.
        Each line has:
            name, code, abbreviation
        """
        def _institution_line_parser(line):
            return {
                'name'         : line[0],
                'code'         : line[1],
                'abbreviation' : line[2],
            }
        return self._import(f, _institution_line_parser, m.Institution)

    def import_venue_groups(self, f):
        """Imports venue groups from a file.
        Each line has:
            name, short_name[, team_capacity]
        """
        def _venue_group_line_parser(line):
            kwargs = {
                'name'       : line[0],
                'short_name' : line[1],
            }
            if len(line) > 2:
                kwargs['team_capacity'] = line[2]
            return kwargs
        return self._import(f, _venue_group_line_parser, m.VenueGroup)

    def import_venues(self, f, auto_create_groups=True):
        """Imports venues from a file, also creating venue groups as needed
        (unless 'auto_create_groups' is False).

        Each line has:
            name, priority, venue_group.name, time
        """

        if auto_create_groups:
            def _venue_group_line_parser(line):
                if not line[2]:
                    return None
                return {
                    'name'       : line[2],
                    'short_name' : line[2][:25],
                }
            counts, errors = self._import(f, _venue_group_line_parser,
                    m.VenueGroup, expect_unique=False)
        else:
            counts = None
            errors = None

        def _venue_line_parser(line):
            return {
                'tournament' : self.tournament,
                'name'       : line[0],
                'priority'   : int(line[1]) if len(line) > 1 else 10,
                'group'      : m.VenueGroup.objects.get(name=line[2]) if len(line) > 2 else None,
                'time'       : line[3] if len(line) > 3 else None,
            }
        counts, errors = self._import(f, _venue_line_parser, m.Venue, counts=counts, errors=errors)

        return counts, errors

    def import_teams(self, f, create_dummy_speakers=False):
        """Imports teams from a file, assigning emoji as needed.
        If 'create_dummy_speakers' is True, also creates dummy speakers."""

        self.initialise_emoji_options()
        def _team_line_parser(line):
            return {
                'name'        : line[0],
                'short_name'  : line[0][:34],
                'institution' : m.Institutions.objects.lookup(line[1]),
                'emoji_seq'   : self.get_emoji()
            }
        counts, errors = self._import(f, _team_line_parser, m.Team)

        if create_dummy_speakers:
            def _speakers_line_parser(line):
                team = m.Teams.objects.get(name=line[0])
                for name in ["1st Speaker", "2nd Speaker", "3rd Speaker", "Reply Speaker"]:
                    yield dict(name=name, team=team)
            counts, errors = self._import(f, _speakers_line_parser, m.Speaker, counts=counts, errors=errors)

    def import_speakers(self, f, auto_create_teams=True):
        """Imports speakers from a file, also creating teams as needed (unless
        'auto_create_teams' is False). Institutions are not created as needed;
        if an institution doesn't exist, an error is raised.

        Each line has:
            name, institution_name, team_name, use_team_name_as_prefix, gender,
                    novice_status.
        """

        if auto_create_teams:
            def _team_line_parser(line):
                return {
                    'tournament'             : self.tournament,
                    'institution'            : m.Institution.objects.lookup(line[1]),
                    'reference'              : line[2],
                    'short_reference'        : line[2][:35],
                    'use_institution_prefix' : int(line[3]) if len(line) > 3 else 0,
                }
            counts, errors = self._import(f, _team_line_parser, m.Team, expect_unique=False)
        else:
            counts = None
            errors = None

        def _speaker_line_parser(line):
            institution = m.Institution.objects.lookup(line[1])
            return {
                'name'   : line[0],
                'team'   : m.Team.objects.get(institution=institution,
                                      reference=line[2], tournament=self.tournament),
                'gender' : self._lookup(self.GENDERS, line[4], "gender") if len(line) > 4 and line[4] else None,
                'novice' : int(line[5]) if len(line) > 5 and line[5] else None,
            }
        counts, errors = self._import(f, _speaker_line_parser, m.Speaker, counts=counts, errors=errors)

        return counts, errors

    def import_adjudicators(self, f, auto_conflict=True):
        """Imports adjudicators from a file. Institutions are not created as
        needed; if an institution doesn't exist, an error is raised. Conflicts
        are created from the same file, if present. If 'auto_conflict' is True
        (default), conflicts are created with adjudicators' own institutions.

        Each line has:
            name, institution, rating, gender, novice, cellphone, email,
                    notes, institution_conflicts, team_conflicts
        """
        def _adjudicator_line_parser(line):
            return {
                'name'        : line[0],
                'institution' : m.Institution.objects.lookup(line[1]),
                'test_score'  : float(line[2]),
                'gender'      : self._lookup(self.GENDERS, line[3], "gender") if len(line) > 3 and line[3] else None,
                'novice'      : int(line[4]) if len(line) > 4 and line[4] else False,
                'phone'       : line[5] if len(line) > 5 else None,
                'email'       : line[6] if len(line) > 6 else None,
                'notes'       : line[7] if len(line) > 7 else None,
            }
        counts, errors = self._import(f, _adjudicator_line_parser, m.Adjudicator)

        def _test_score_line_parser(line):
            institution = m.Institution.objects.lookup(line[1])
            return {
                'adjudicator' : m.Adjudicator.objects.get(name=line[0], institution=institution),
                'score'       : float(line[2]),
                'round'       : None,
            }
        counts, errors = self._import(f, _test_score_line_parser, m.AdjudicatorTestScoreHistory,
                counts=counts, errors=errors)

        def _own_institution_conflict_parser(line):
            institution = m.Institution.objects.lookup(line[1])
            return {
                'adjudicator' : m.Adjudicator.objects.get(name=line[0], institution=institution),
                'institution' : institution,
            }
        counts, errors = self._import(f, _own_institution_conflict_parser, m.AdjudicatorInstitutionConflict,
                counts=counts, errors=errors)

        def _institution_conflict_parser(line):
            if len(line) <= 8 or not line[8]:
                return
            adj_inst = m.Institution.objects.lookup(line[1])
            adjudicator = m.Adjudicator.objects.get(name=line[0], institution=adj_inst)
            for institution_name in line[8].split(","):
                institution_name = institution_name.strip()
                institution = m.Institution.objects.lookup(institution_name)
                yield {
                    'adjudicator' : adjudicator,
                    'institution' : institution,
                }
        counts, errors = self._import(f, _institution_conflict_parser, m.AdjudicatorInstitutionConflict,
                counts=counts, errors=errors)

        def _team_conflict_parser(line):
            if len(line) <= 9 or not line[9]:
                return
            adj_inst = m.Institution.objects.lookup(line[1])
            adjudicator = m.Adjudicator.objects.get(name=line[0], institution=adj_inst)
            for team_name in line[9].split(","):
                team = m.Team.objects.lookup(team_name)
                yield {
                    'adjudicator' : adjudicator,
                    'team'        : team,
                }
        counts, errors = self._import(f, _team_conflict_parser, m.AdjudicatorConflict,
                counts=counts, errors=errors)

        return counts, errors

    def import_motions(self, f):
        """Imports motions from a file.
        Each line has:
            round, motion_seq, reference, text
        """
        def _motion_line_parser(line):
            return {
                'round': m.Round.objects.lookup(line[0], tournament=self.tournament),
                'seq': int(line[1]),
                'reference': line[2],
                'text': line[3],
            }
        return self._import(f, _motion_line_parser, m.Motion)

    def import_sides(self, f):
        """Imports sides from a file.
        Each line has:
            team_name, side_for_round1, side_for_round2, ...
        """
        def _side_line_parser(line):
            team = m.Team.objects.lookup(line[0])
            for seq, side in enumerate(line[1:], start=1):
                yield {
                    'round': m.Round.objects.get(seq=seq),
                    'team' : team,
                    'position': self._lookup(self.TEAM_POSITIONS, side),
                }

    def import_config(self, f):
        VALUE_TYPES = {"string": str, "int": int, "float": float, "bool": bool}
        def _config_line_parser(line):
            kwargs = dict()
            key = line[0]
            try:
                coerce = VALUE_TYPES[line[1]]
            except KeyError:
                raise ValueError("Unrecognized value type in config: {0:r}".format(line[1]))
            value = coerce(line[2])

    def auto_make_rounds(self, num_rounds):
        """Makes the number of rounds specified. The first one is random and the
        rest are all power-paired. The last one is silent. This is intended as a
        convenience function. For anything more complicated, the user should use
        import_rounds() instead."""
        for i in range(1, num_rounds+1):
            m.Round(
                tournament=self.tournament,
                seq=i,
                name='Round %d' % i,
                abbreviation='R%d' % i,
                draw_type=m.Round.DRAW_RANDOM if (i == 1) else m.Round.DRAW_POWERPAIRED,
                feedback_weight=min((i-1)*0.1, 0.5),
                silent=(i == num_rounds),
            ).save()
        self.logger.info("Auto-made %d rounds", num_rounds)
