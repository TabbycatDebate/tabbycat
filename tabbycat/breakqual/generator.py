import logging

from breakqual.models import BreakCategory

# These imports add the break generators in those files to the registry.
from . import aida  # noqa: F401
from . import base

logger = logging.getLogger(__name__)


def BreakGenerator(category, **kwargs):  # noqa: N802
    klass = base.registry[category.rule]
    return klass(category, **kwargs)


# Verify that the available generators match the choices in the BreakCategory model
generator_keys = set(base.registry.keys())
model_choices = set(key for key, _ in BreakCategory.BREAK_QUALIFICATION_CHOICES)
if generator_keys != model_choices:
    logger.error("The generators in the registry don't match the choices for the "
                 "'rule' field of the BreakCategory model.")
    logger.error("In the registry, we have: " + str(generator_keys))
    logger.error("In the model, we have: " + str(model_choices))
