"""Break generators relating to the Western Australia Debating League (WADL)."""

import logging

from .base import register, BaseBreakGenerator

logger = logging.getLogger(__name__)


class WadlDivisionWinnersFirstBreakGenerator(BaseBreakGenerator):
    key = "wadldivfirst"


class WadlDivisionWinnersGuaranteedBreakGenerator(BaseBreakGenerator):
    key = "wadl-divguaranteed"
