from .standings import annotate_team_standings
from .teams import TeamStandingsGenerator

presets = {
    "australs": ('points', 'speaker_score'),
    "nz"      : ('points', 'wbw', 'speaker_score', 'wbw', 'draw_strength', 'wbw'),
    "wadl"    : ('points', 'wbw', 'margins', 'speaker_score'),
    "test"    : ('points', 'wbw', 'draw_strength', 'wbw', 'speaker_score', 'wbw', 'margins', 'wbw'),
}