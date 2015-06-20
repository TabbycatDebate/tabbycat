from base import BaseTournamentDataImporter, TournamentDataImporterError
import debate.models as m
import csv

class AnorakTournamentDataImporter(BaseTournamentDataImporter):
    """Anorak: The original tournament data format."""

    ROUND_STAGES = {
        ("preliminary", "p"): m.Round.STAGE_PRELIMINARY,
        ("elimination", "break", "e", "b"): m.Round.STAGE_ELIMINATION,
    }

    ROUND_DRAW_TYPES = {
        ("random", "r"): m.Round.DRAW_RANDOM,
        ("manual", "m"): m.Round.DRAW_MANUAL,
        ("round robin", "d"): m.Round.DRAW_ROUNDROBIN,
        ("power paired", "p"): m.Round.DRAW_POWERPAIRED,
        ("first elimination", "1st elimination", "1e", "f"): m.Round.DRAW_FIRSTBREAK,
        ("subsequent elimination", "2nd elimination", "2e", "b"): m.Round.DRAW_BREAK,
    }

    GENDERS = {
        ("male", "m"): m.Person.GENDER_MALE,
        ("female", "f"): m.Person.GENDER_FEMALE,
        ("other", "o"): m.Person.GENDER_OTHER,
    }

    TEAM_POSITIONS = {
        ("affirmative", "aff", "a"): m.TeamPositionAllocation.POSITION_AFFIRMATIVE,
        ("negative", "aff", "n"): m.TeamPositionAllocation.POSITION_NEGATIVE,
    }

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

    def import_regions(self, f):
        """Imports regions from a file.
        Each line has:
            name
        """
        def _region_line_parser(line):
            kwargs = {
                'name'       : line[0],
            }
            return kwargs
        return self._import(f, _region_line_parser, m.Region)

    def import_institutions(self, f, auto_create_regions=False):
        """Imports institutions from a file, also creating regions as needed
        (unless 'auto_create_regions' is False)
        Each line has:
            name, code, abbreviation, region
        """
        if auto_create_regions:
            def _region_line_parser(line):
                if not line[3]:
                    return None
                return {
                    'name': line[3],
                }
            counts, errors = self._import(f, _region_line_parser,
                    m.Region, expect_unique=False)
        else:
            counts = None
            errors = None

        def _institution_line_parser(line):
            return {
                'name'         : line[0],
                'code'         : line[1],
                'abbreviation' : line[2],
                'region'       : m.Region.objects.get(name=line[3]) if len(line) > 3  and line[3] else None,
            }
        counts, errors = self._import(f, _institution_line_parser, m.Institution, counts=counts, errors=errors)

        return counts, errors

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
                'group'      : m.VenueGroup.objects.get(name=line[2]) if len(line) > 2 and line[2] else None,
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
                'tournament'  : self.tournament,
                'test_score'  : float(line[2]),
                'gender'      : self._lookup(self.GENDERS, line[3], "gender") if len(line) > 3 and line[3] else None,
                'independent' : bool(line[4]) if len(line) > 4 and line[4] else False,
                'novice'      : int(line[5]) if len(line) > 5 and line[5] else False,
                'phone'       : line[6] if len(line) > 6 else None,
                'email'       : line[7] if len(line) > 7 else None,
                'notes'       : line[8] if len(line) > 8 else None,
            }
        counts, errors = self._import(f, _adjudicator_line_parser, m.Adjudicator)

        def _test_score_line_parser(line):
            institution = m.Institution.objects.lookup(line[1])
            return {
                'adjudicator' : m.Adjudicator.objects.get(name=line[0], institution=institution, tournament=self.tournament),
                'score'       : float(line[2]),
                'round'       : None,
            }
        counts, errors = self._import(f, _test_score_line_parser, m.AdjudicatorTestScoreHistory,
                counts=counts, errors=errors)

        def _own_institution_conflict_parser(line):
            institution = m.Institution.objects.lookup(line[1])
            return {
                'adjudicator' : m.Adjudicator.objects.get(name=line[0], institution=institution, tournament=self.tournament),
                'institution' : institution,
            }
        counts, errors = self._import(f, _own_institution_conflict_parser, m.AdjudicatorInstitutionConflict,
                counts=counts, errors=errors)

        def _institution_conflict_parser(line):
            if len(line) <= 9 or not line[9]:
                return
            adj_inst = m.Institution.objects.lookup(line[1])
            adjudicator = m.Adjudicator.objects.get(name=line[0], institution=adj_inst, tournament=self.tournament)
            for institution_name in line[9].split(","):
                institution_name = institution_name.strip()
                institution = m.Institution.objects.lookup(institution_name)
                yield {
                    'adjudicator' : adjudicator,
                    'institution' : institution,
                }
        counts, errors = self._import(f, _institution_conflict_parser, m.AdjudicatorInstitutionConflict,
                counts=counts, errors=errors)

        def _team_conflict_parser(line):
            if len(line) <= 10 or not line[10]:
                return
            adj_inst = m.Institution.objects.lookup(line[1])
            adjudicator = m.Adjudicator.objects.get(name=line[0], institution=adj_inst, tournament=self.tournament)
            for team_name in line[10].split(","):
                team = m.Team.objects.lookup(team_name)
                yield {
                    'adjudicator' : adjudicator,
                    'team'        : team,
                }
        counts, errors = self._import(f, _team_conflict_parser, m.AdjudicatorConflict,
                counts=counts, errors=errors)

        def _adj_conflict_parser(line):
            if len(line) <= 11 or not line[11]:
                return
            adj_inst = m.Institution.objects.lookup(line[1])
            adjudicator = m.Adjudicator.objects.get(name=line[0], institution=adj_inst, tournament=self.tournament)
            for adj_name in line[11].split(","):
                conflicting_adj = m.Adjudicator.objects.get(name=adj_name)
                print conflicting_adj
                yield {
                    'adjudicator'           : adjudicator,
                    'conflict_adjudicator'  : conflicting_adj,
                }
        counts, errors = self._import(f, _adj_conflict_parser, m.AdjudicatorAdjudicatorConflict,
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
        """Imports configuration settings from a file.
        Each line has:
            key, value_type, value
        """
        def _bool(val):
            if val.lower() in ["true", "1"]:
                return True
            elif val.lower() in ["false", "0"]:
                return False
            else:
                raise ValueError("Unrecognized boolean value: %r" % val)
        coercefuncs = {"string": str, "int": int, "float": float, "bool": _bool,
            "str": str}

        reader = csv.reader(f)
        count = 0
        errors = TournamentDataImporterError()
        if self.header_row:
            reader.next()

        for lineno, line in enumerate(reader, start=2 if self.header_row else 1):
            try:
                key, value_type, value = line
            except ValueError as e:
                errors.add(lineno, m.Config, "Couldn't parse line: " + str(e))
                continue
            if value:
                try:
                    coercefunc = coercefuncs[value_type]
                except KeyError:
                    errors.add(lineno, m.Config, "Unrecognized value type: %r" % value_type)
                    continue
                try:
                    value = coercefunc(value)
                except ValueError as e:
                    errors.add(lineno, m.Config, "Invalid value for type %r: %r" % (value_type, value))
                    continue
                self.tournament.config.set(key, value)
                count += 1
                self.logger.debug("Made config %r = %r" % (key, value))

        if errors:
            if self.strict:
                for message in errors.itermessages():
                    self.logger.error(message)
                raise errors
            else:
                for message in errors.itermessages():
                    self.logger.warning(message)

        return {m.Config: count}, errors

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
