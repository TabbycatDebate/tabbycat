from api.query_serializers import SpeakerStandingsParamsSerializer, TeamStandingsParamsSerializer
from api.views import get_metrics_params
from django.test import SimpleTestCase

from standings.speakers import SpeakerStandingsGenerator
from standings.teams import TeamStandingsGenerator


class StandingsMetricSchemaTests(SimpleTestCase):

    def test_metric_enums_match_parameter_validation(self):
        for generator, serializer_class in (
            (SpeakerStandingsGenerator, SpeakerStandingsParamsSerializer),
            (TeamStandingsGenerator, TeamStandingsParamsSerializer),
        ):
            serializer = serializer_class()
            for parameter in get_metrics_params(generator):
                with self.subTest(generator=generator.__name__, parameter=parameter.name):
                    self.assertEqual(parameter.type['items']['enum'],
                                     list(serializer.fields[parameter.name].child.choices))

    def test_speaker_schema_excludes_reply_metrics(self):
        for parameter in get_metrics_params(SpeakerStandingsGenerator):
            self.assertFalse(any(key.startswith('replies_') for key in parameter.type['items']['enum']))

    def test_team_extra_metrics_include_draw_strength_by_rank(self):
        parameters = {parameter.name: parameter for parameter in get_metrics_params(TeamStandingsGenerator)}
        self.assertNotIn('draw_strength_rank', parameters['metrics'].type['items']['enum'])
        self.assertIn('draw_strength_rank', parameters['extra_metrics'].type['items']['enum'])
