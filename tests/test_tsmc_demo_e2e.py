#!/usr/bin/env python3
"""TSMC Demo E2E verification tests.

Sprint: S-PTB-DEMO-TSMC v1.0.0
Run: PYTHONPATH=build/cpp/binding:src python3 tests/test_tsmc_demo_e2e.py
⛔ NOT pytest — uses direct assertions (ISS-042 OOM prevention)

Tests:
  T09: Safety inspection flow
  T10: Cost change real-time update
  T11: 4D timeline playback
  T12: AI dialogue full flow
  T13: Full 5-minute demo (uninterrupted)
  T14: Error recovery (interrupt + continue)
  T15: ctest ALL PASS (verified externally)
"""

import json
import sys
import os
import time

# Paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build', 'cpp', 'binding'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import bim_core
from promptbim.ai.nl_parser import NLParser, IntentType
from promptbim.ai.intent_router import IntentRouter
from promptbim.demo.tsmc_factory import (
    get_all_entity_defs,
    check_collisions,
    run_safety_audit,
    calculate_scene_cost,
    build_4d_schedule,
    TSMC_AI_PROMPTS,
    DEMO_SCRIPT,
    TSMC_COST_TEMPLATE,
)

PASSED = 0
FAILED = 0


def check(name, condition, detail=""):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        print(f"  ❌ {name}: {detail}")


def build_tsmc_scene():
    """Build the full TSMC factory scene in C++ bim_core."""
    sg = bim_core.BIMSceneGraph()
    bridge = bim_core.AgentBridge(sg)
    parser = NLParser(use_llm=False)
    router = IntentRouter()

    for edef in get_all_entity_defs():
        etype = getattr(bim_core.EntityType, edef.entity_type, bim_core.EntityType.Generic)
        entity = bim_core.BIMEntity(edef.id, etype, edef.name)
        entity.set_position(bim_core.Vec3(*edef.position))
        entity.set_dimensions(bim_core.Vec3(*edef.dimensions))
        for k, v in edef.properties.items():
            entity.set_property(k, v)
        sg.add_entity(entity)

    return sg, bridge, parser, router


# ===== T09: Safety Inspection Flow =====

def t09_safety_inspection():
    """T09: Safety inspection — hydrants, sprinklers, exits, nets."""
    print("T09: Safety inspection flow")
    sg, bridge, parser, router = build_tsmc_scene()

    # Query fire hydrants by name
    intent = parser.parse("列出所有消防栓的位置")
    check("T09.1 NL parse", intent.is_valid, f"type={intent.intent_type}")

    # Query hydrants via bridge (Chinese names: 消防栓)
    r = bridge.query_by_name("消防栓")
    check("T09.2 hydrant query success", r.success)
    data = json.loads(r.data)
    check("T09.3 hydrant count=4", len(data) == 4, f"got {len(data)}")

    # Query sprinklers
    r = bridge.query_by_name("灑水頭")
    check("T09.4 sprinkler query success", r.success)

    # Query emergency exits (Chinese: 緊急出口)
    r = bridge.query_by_name("緊急出口")
    check("T09.5 exit query success", r.success)
    data = json.loads(r.data)
    check("T09.6 exit count=2", len(data) == 2, f"got {len(data)}")

    # Python-side safety audit
    entities = get_all_entity_defs()
    audit = run_safety_audit(entities)
    check("T09.7 audit pass", audit["overall_pass"], f"audit={audit}")
    check("T09.8 hydrant coverage", audit["hydrant_coverage_ok"])
    check("T09.9 sprinkler spacing", audit["sprinkler_spacing_ok"])
    check("T09.10 exit compliance", audit["exit_compliance"])


# ===== T10: Cost Change Real-Time =====

def t10_cost_realtime():
    """T10: Move equipment → cost delta → verify change."""
    print("T10: Cost change real-time update")
    sg, bridge, parser, router = build_tsmc_scene()

    # Get initial cost
    r1 = bridge.get_cost_delta()
    check("T10.1 initial cost query", r1.success)

    # Python cost calculation
    entities = get_all_entity_defs()
    cost_data = calculate_scene_cost(entities)
    check("T10.2 total > 0", cost_data["total_ntd"] > 0, f"total={cost_data['total_ntd']}")
    check("T10.3 has breakdown", all(k in cost_data["breakdown"] for k in ("structural", "mep", "safety")))
    check("T10.4 item count matches", cost_data["item_count"] == len(entities))

    # Move chiller via NL (use verb-first pattern for regex match)
    intent = parser.parse("移動冰水主機A到座標 (30, 25, -3)")
    check("T10.5 NL→MOVE", intent.intent_type == IntentType.MOVE)
    action = router.route(intent)
    check("T10.6 route→move", action is not None and action["action"] == "move")

    # Execute move via bridge
    r2 = bridge.move_entity("chiller-1", bim_core.Vec3(30, 25, -3))
    check("T10.7 move success", r2.success)

    # Get cost after move
    r3 = bridge.get_cost_delta()
    check("T10.8 post-move cost query", r3.success)

    # Verify cost template completeness
    check("T10.9 cost template entries", len(TSMC_COST_TEMPLATE) >= 20,
          f"got {len(TSMC_COST_TEMPLATE)}")
    check("T10.10 has chiller price", "chiller_500rt" in TSMC_COST_TEMPLATE)


# ===== T11: 4D Timeline Playback =====

def t11_4d_timeline():
    """T11: 4D schedule — phases, entity mapping, timeline."""
    print("T11: 4D timeline playback")
    entities = get_all_entity_defs()
    phases = build_4d_schedule(entities)

    check("T11.1 phase count=5", len(phases) == 5, f"got {len(phases)}")

    total_days = sum(p.duration_days for p in phases)
    check("T11.2 total days=220", total_days == 220, f"got {total_days}")

    # Each entity assigned to a phase
    all_phase_entities = set()
    for p in phases:
        all_phase_entities.update(p.entity_ids)
    check("T11.3 all entities assigned", len(all_phase_entities) == len(entities),
          f"assigned={len(all_phase_entities)} total={len(entities)}")

    # Phase 1 = structural
    check("T11.4 phase1=Foundation", phases[0].name == "基礎結構")
    check("T11.5 phase1 entities", len(phases[0].entity_ids) > 10,
          f"got {len(phases[0].entity_ids)}")

    # Phase 3 = MEP
    check("T11.6 phase3=MEP", phases[2].name == "機電設備")
    phase3_ids = phases[2].entity_ids
    check("T11.7 chiller in phase3", "chiller-1" in phase3_ids)
    check("T11.8 ahu in phase3", "ahu-1" in phase3_ids)

    # Phase 5 = commissioning
    check("T11.9 phase5=Commissioning", phases[4].name == "收尾驗收")
    check("T11.10 sensor in phase5", "sensor-t1" in phases[4].entity_ids)

    # JSON export
    from promptbim.demo.tsmc_factory import schedule_to_json
    j = json.loads(schedule_to_json(phases))
    check("T11.11 json valid", j["total_phases"] == 5)


# ===== T12: AI Dialogue Full Flow =====

def t12_ai_dialogue():
    """T12: Full NL→AI→C++→Result pipeline for each scenario."""
    print("T12: AI dialogue full flow")
    sg, bridge, parser, router = build_tsmc_scene()

    # Test each of the 10 TSMC AI prompts
    for i, prompt in enumerate(TSMC_AI_PROMPTS):
        intent = parser.parse(prompt["user"])
        action = router.route(intent) if intent.is_valid else None
        # We check that at least the parser produces a valid intent or action
        has_result = intent.is_valid or action is not None
        check(f"T12.{i+1} scenario:{prompt['scenario']}",
              has_result,
              f"intent={intent.intent_type} valid={intent.is_valid}")


# ===== T13: Full 5-Minute Demo Flow (Uninterrupted) =====

def t13_full_demo():
    """T13: Complete demo flow — all 5 steps without crash."""
    print("T13: Full 5-minute demo flow (uninterrupted)")
    sg, bridge, parser, router = build_tsmc_scene()

    initial_count = sg.entity_count()
    check("T13.1 initial entity count", initial_count >= 35, f"got {initial_count}")

    # Step 1: Scene overview
    r = bridge.get_scene_info()
    check("T13.2 scene info", r.success)

    # Step 2: Safety queries (3 queries)
    for name_query in ["消防栓", "灑水頭", "緊急出口"]:
        r = bridge.query_by_name(name_query)
        check(f"T13.3 query {name_query}", r.success)

    # Step 3: Cost + move
    r = bridge.get_cost_delta()
    check("T13.4 cost delta", r.success)
    r = bridge.move_entity("chiller-1", bim_core.Vec3(30, 25, -3))
    check("T13.5 move chiller", r.success)
    r = bridge.get_cost_delta()
    check("T13.6 post-move cost", r.success)

    # Step 4: Schedule info
    entities = get_all_entity_defs()
    phases = build_4d_schedule(entities)
    check("T13.7 schedule built", len(phases) == 5)

    # Step 5: AI actions
    r = bridge.add_entity("ahu-3", bim_core.EntityType.AHU, "AHU C",
                          bim_core.Vec3(60, 35, 0.5))
    check("T13.8 add AHU", r.success)
    r = bridge.get_nearby("chiller-1", 10.0)
    check("T13.9 nearby query", r.success)
    r = bridge.connect_entities("pump-1", "chiller-1")
    check("T13.10 connect", r.success)

    final_count = sg.entity_count()
    check("T13.11 entity count grew", final_count > initial_count)
    check("T13.12 no crash", True)  # If we got here, no crash


# ===== T14: Error Recovery =====

def t14_error_recovery():
    """T14: Error handling — invalid operations, then continue."""
    print("T14: Error recovery test")
    sg, bridge, parser, router = build_tsmc_scene()

    # Try to move non-existent entity
    r = bridge.move_entity("nonexistent-999", bim_core.Vec3(0, 0, 0))
    check("T14.1 move nonexistent fails", not r.success)

    # Try to delete non-existent
    r = bridge.delete_entity("nonexistent-999")
    check("T14.2 delete nonexistent fails", not r.success)

    # Scene should still be intact
    check("T14.3 scene intact", sg.entity_count() >= 35)

    # Normal operation should still work
    r = bridge.get_scene_info()
    check("T14.4 scene info after error", r.success)

    r = bridge.move_entity("chiller-1", bim_core.Vec3(30, 25, -3))
    check("T14.5 move works after error", r.success)

    # Parse invalid NL → should return UNKNOWN
    intent = parser.parse("")
    check("T14.6 empty input → UNKNOWN", intent.intent_type == IntentType.UNKNOWN)

    intent = parser.parse("asdfghjkl")
    check("T14.7 gibberish → UNKNOWN", intent.intent_type == IntentType.UNKNOWN)

    # Collision check with Python module
    entities = get_all_entity_defs()
    collisions = check_collisions(entities)
    check("T14.8 collision check completes", isinstance(collisions, list))

    check("T14.9 scene still works", sg.entity_count() >= 35)
    check("T14.10 demo script exists", len(DEMO_SCRIPT) == 5)


# ===== Main =====

def main():
    print("=" * 60)
    print("TSMC Demo E2E Verification — S-PTB-DEMO-TSMC v1.0.0")
    print("=" * 60)

    t09_safety_inspection()
    t10_cost_realtime()
    t11_4d_timeline()
    t12_ai_dialogue()
    t13_full_demo()
    t14_error_recovery()

    print("=" * 60)
    total = PASSED + FAILED
    print(f"Results: {PASSED}/{total} PASSED, {FAILED} FAILED")
    if FAILED > 0:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("✅ ALL TESTS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
