"""Bridge between PySide6 GUI and C++ bim_core module.

Provides a singleton-like BIMCoreBridge that owns the SceneGraph,
AgentBridge, PropertyManager and CostCalculator instances.  All GUI
widgets read from / write to the same bridge so they stay in sync.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from promptbim.debug import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("gui.bim_core_bridge")

# Ensure the build output is on sys.path so `import bim_core` works
_BUILD_BINDING = Path(__file__).resolve().parents[3] / "build" / "cpp" / "binding"
if str(_BUILD_BINDING) not in sys.path:
    sys.path.insert(0, str(_BUILD_BINDING))

try:
    import bim_core
    BIM_CORE_AVAILABLE = True
    logger.info("bim_core loaded from %s", bim_core.__doc__)
except ImportError:
    BIM_CORE_AVAILABLE = False
    logger.warning("bim_core not available — C++ bridge disabled")


class BIMCoreBridge(QObject):
    """Central gateway between the Qt GUI and the C++ bim_core module.

    Signals are emitted whenever the scene changes so widgets can refresh.
    """

    scene_changed = Signal()        # entity added/removed/moved
    entity_selected = Signal(str)   # entity id
    cost_updated = Signal()         # cost recalculated

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        if not BIM_CORE_AVAILABLE:
            self._scene = None
            self._agent = None
            self._prop_mgr = None
            self._cost_calc = None
            return

        self._scene = bim_core.BIMSceneGraph()
        self._agent = bim_core.AgentBridge(self._scene)
        self._prop_mgr = bim_core.PropertyManager()
        self._cost_calc = bim_core.CostCalculator(self._prop_mgr)
        logger.info(
            "BIMCoreBridge ready — materials=%d",
            self._prop_mgr.material_count(),
        )

    @property
    def available(self) -> bool:
        return BIM_CORE_AVAILABLE and self._scene is not None

    @property
    def scene(self) -> "bim_core.BIMSceneGraph | None":
        return self._scene

    @property
    def agent(self) -> "bim_core.AgentBridge | None":
        return self._agent

    @property
    def property_manager(self) -> "bim_core.PropertyManager | None":
        return self._prop_mgr

    @property
    def cost_calculator(self) -> "bim_core.CostCalculator | None":
        return self._cost_calc

    # ---- high-level helpers ----

    def load_demo_scene(self) -> None:
        """Populate the scene graph with a TSMC-style demo scene."""
        if not self.available:
            return
        self._scene.clear()

        demo_entities = [
            ("chiller-1", bim_core.EntityType.Chiller, "Chiller-A",
             (5.0, 10.0, 0.0), (3.0, 2.0, 2.5)),
            ("chiller-2", bim_core.EntityType.Chiller, "Chiller-B",
             (5.0, 15.0, 0.0), (3.0, 2.0, 2.5)),
            ("tower-1", bim_core.EntityType.CoolingTower, "CoolingTower-1",
             (20.0, 10.0, 0.0), (2.5, 2.5, 4.0)),
            ("pump-1", bim_core.EntityType.Pump, "CW-Pump-1",
             (12.0, 10.0, 0.0), (1.0, 0.8, 0.8)),
            ("ahu-1", bim_core.EntityType.AHU, "AHU-1F",
             (15.0, 5.0, 0.0), (4.0, 2.0, 2.0)),
            ("column-1", bim_core.EntityType.Column, "Column-A1",
             (0.0, 0.0, 0.0), (0.6, 0.6, 4.0)),
            ("column-2", bim_core.EntityType.Column, "Column-A2",
             (10.0, 0.0, 0.0), (0.6, 0.6, 4.0)),
            ("column-3", bim_core.EntityType.Column, "Column-B1",
             (0.0, 10.0, 0.0), (0.6, 0.6, 4.0)),
            ("column-4", bim_core.EntityType.Column, "Column-B2",
             (10.0, 10.0, 0.0), (0.6, 0.6, 4.0)),
            ("wall-1", bim_core.EntityType.Wall, "ExtWall-North",
             (5.0, 20.0, 0.0), (20.0, 0.3, 4.0)),
            ("wall-2", bim_core.EntityType.Wall, "ExtWall-South",
             (5.0, 0.0, 0.0), (20.0, 0.3, 4.0)),
            ("slab-1", bim_core.EntityType.Slab, "Slab-1F",
             (10.0, 10.0, 0.0), (20.0, 20.0, 0.3)),
            ("slab-2", bim_core.EntityType.Slab, "Slab-2F",
             (10.0, 10.0, 4.0), (20.0, 20.0, 0.3)),
            ("pipe-1", bim_core.EntityType.Pipe, "CW-Pipe-Main",
             (10.0, 10.0, 1.0), (8.0, 0.15, 0.15)),
            ("duct-1", bim_core.EntityType.Duct, "SA-Duct-1F",
             (15.0, 8.0, 3.5), (6.0, 0.6, 0.4)),
            ("exhaust-1", bim_core.EntityType.ExhaustStack, "ExhaustStack-1",
             (20.0, 20.0, 0.0), (1.0, 1.0, 8.0)),
            ("valve-1", bim_core.EntityType.Valve, "CW-Valve-1",
             (8.0, 10.0, 1.0), (0.3, 0.3, 0.3)),
            ("sensor-1", bim_core.EntityType.Sensor, "TempSensor-1F",
             (15.0, 10.0, 2.5), (0.1, 0.1, 0.1)),
            ("door-1", bim_core.EntityType.Door, "MainEntry",
             (5.0, 0.0, 0.0), (1.2, 0.1, 2.4)),
            ("window-1", bim_core.EntityType.Window, "Window-N1",
             (8.0, 20.0, 1.0), (1.5, 0.1, 1.5)),
            ("stair-1", bim_core.EntityType.Stair, "Stair-Core",
             (18.0, 2.0, 0.0), (3.0, 6.0, 4.0)),
            ("beam-1", bim_core.EntityType.Beam, "Beam-A",
             (5.0, 0.0, 3.8), (10.0, 0.4, 0.6)),
        ]
        for eid, etype, name, pos, dims in demo_entities:
            entity = bim_core.BIMEntity(eid, etype, name)
            entity.set_position(bim_core.Vec3(*pos))
            entity.set_dimensions(bim_core.Vec3(*dims))
            self._scene.add_entity(entity)

        # Connections
        self._scene.connect_entities("chiller-1", "pump-1")
        self._scene.connect_entities("pump-1", "tower-1")
        self._scene.connect_entities("chiller-1", "pipe-1")

        logger.info("Demo scene loaded: %d entities", self._scene.entity_count())
        self.scene_changed.emit()
        self.cost_updated.emit()

    def execute_action(self, action_json: str) -> dict:
        """Execute an agent action via JSON and return parsed result."""
        if not self.available:
            return {"success": False, "message": "bim_core not available"}
        result_json = self._agent.execute_json(action_json)
        self.scene_changed.emit()
        self.cost_updated.emit()
        try:
            return json.loads(result_json)
        except (json.JSONDecodeError, TypeError):
            return {"success": True, "message": result_json}

    def get_scene_entities(self) -> list[dict]:
        """Return all entities as a list of dicts."""
        if not self.available:
            return []
        info_json = self._scene.to_json()
        try:
            data = json.loads(info_json)
            return data.get("entities", [])
        except (json.JSONDecodeError, TypeError):
            return []

    def get_cost_summary(self) -> dict:
        """Return cost summary from CostCalculator."""
        if not self.available:
            return {}
        try:
            result_json = self._agent.get_cost_delta()
            return json.loads(result_json.data) if result_json.data else {}
        except (json.JSONDecodeError, TypeError, AttributeError, RuntimeError):
            return {"total_cost": self._scene.total_cost(), "currency": "NT$"}

    def get_scene_info(self) -> dict:
        """Return scene info from AgentBridge."""
        if not self.available:
            return {}
        result = self._agent.get_scene_info()
        try:
            return json.loads(result.data) if result.data else {}
        except (json.JSONDecodeError, TypeError):
            return {"message": result.message}
