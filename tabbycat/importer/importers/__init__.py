from .base import DUPLICATE_INFO, TournamentDataImporterFatal, TournamentDataImporterError

from . import anorak
from . import boots

importer_registry = {
    'anorak': anorak.AnorakTournamentDataImporter,
    'boots': boots.BootsTournamentDataImporter,
}
