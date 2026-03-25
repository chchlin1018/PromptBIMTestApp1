"""Auto-register all component definitions into the ComponentRegistry."""

from promptbim.bim.components.envelope.defs import ENVELOPE_COMPONENTS
from promptbim.bim.components.fixtures.defs import FIXTURE_COMPONENTS
from promptbim.bim.components.interior.defs import INTERIOR_COMPONENTS
from promptbim.bim.components.mep.defs import MEP_COMPONENTS
from promptbim.bim.components.openings.defs import OPENING_COMPONENTS
from promptbim.bim.components.registry import ComponentRegistry
from promptbim.bim.components.site.defs import SITE_COMPONENTS
from promptbim.bim.components.structural.defs import STRUCTURAL_COMPONENTS
from promptbim.bim.components.vertical_transport.defs import VERTICAL_TRANSPORT_COMPONENTS

_ALL_COMPONENTS = (
    STRUCTURAL_COMPONENTS
    + ENVELOPE_COMPONENTS
    + INTERIOR_COMPONENTS
    + OPENING_COMPONENTS
    + VERTICAL_TRANSPORT_COMPONENTS
    + MEP_COMPONENTS
    + FIXTURE_COMPONENTS
    + SITE_COMPONENTS
)


def load_all_components() -> int:
    """Register all built-in components. Returns the total count."""
    ComponentRegistry.register_many(_ALL_COMPONENTS)
    return ComponentRegistry.count()
