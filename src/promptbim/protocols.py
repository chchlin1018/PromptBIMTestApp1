"""ABC/Protocol interfaces for PromptBIM — T12 Architecture improvement.

Defines structural typing protocols and abstract base classes
for the core PromptBIM abstractions:

- BaseAgentABC: ABC for all 7 agents
- BIMEntityProtocol: Protocol for entity-like objects
- SceneQueryProtocol: Protocol for scene query implementations
- CostEngineProtocol: Protocol for cost estimation
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from promptbim.bim.entity_registry import EntityRecord
    from promptbim.bim.scene_query import QueryResult
    from promptbim.schemas.plan import BuildingPlan


# ---------------------------------------------------------------------------
# ABC: BaseAgentABC
# ---------------------------------------------------------------------------

class BaseAgentABC(abc.ABC):
    """Abstract base class for all PromptBIM agents.

    All 7 agents (Enhancer, Planner, Builder, Checker, Modifier,
    LandReader, Orchestrator) should conform to this interface.
    """

    @abc.abstractmethod
    def run(self, user_message: str) -> "AgentResponse":
        """Execute the agent with a user message and return a response."""
        ...

    @property
    @abc.abstractmethod
    def agent_name(self) -> str:
        """Return the agent's display name."""
        ...


# ---------------------------------------------------------------------------
# Protocol: BIMEntityProtocol
# ---------------------------------------------------------------------------

@runtime_checkable
class BIMEntityProtocol(Protocol):
    """Structural protocol for BIM entity-like objects.

    Any object with these attributes is considered a BIM entity.
    """

    @property
    def entity_id(self) -> str: ...

    @property
    def entity_type(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def position(self) -> tuple[float, float, float]: ...


# ---------------------------------------------------------------------------
# Protocol: SceneQueryProtocol
# ---------------------------------------------------------------------------

@runtime_checkable
class SceneQueryProtocol(Protocol):
    """Protocol for scene query implementations."""

    def query_scene(
        self,
        plan: "BuildingPlan",
        entity_type: str | None = None,
    ) -> "QueryResult": ...

    def get_entity_position(
        self,
        plan: "BuildingPlan",
        entity_id: str,
    ) -> tuple[float, float, float] | None: ...

    def find_nearby_entities(
        self,
        plan: "BuildingPlan",
        position: tuple[float, float, float],
        radius: float,
    ) -> "QueryResult": ...


# ---------------------------------------------------------------------------
# Protocol: CostEngineProtocol
# ---------------------------------------------------------------------------

@runtime_checkable
class CostEngineProtocol(Protocol):
    """Protocol for cost estimation engines."""

    def estimate(self, plan: "BuildingPlan") -> "CostEstimate": ...


# ---------------------------------------------------------------------------
# Protocol: SceneOperateProtocol
# ---------------------------------------------------------------------------

@runtime_checkable
class SceneOperateProtocol(Protocol):
    """Protocol for scene manipulation operations."""

    def move_entity(
        self,
        plan: "BuildingPlan",
        entity_id: str,
        dx: float,
        dy: float,
        dz: float,
    ) -> "OperateResult": ...

    def rotate_entity(
        self,
        plan: "BuildingPlan",
        entity_id: str,
        angle_degrees: float,
    ) -> "OperateResult": ...
