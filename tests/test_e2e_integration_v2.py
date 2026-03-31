#!/usr/bin/env python3
"""End-to-end integration tests: NL → AI → C++ bim_core → Qt update.

Sprint: S-PTB-INTEGRATION v0.10.0
Run: PYTHONPATH=build/cpp/binding:src python3 tests/test_e2e_integration_v2.py
⛔ NOT pytest — uses direct assertions (ISS-042 OOM prevention)
"""

import json
import sys
import os

# Paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build', 'cpp', 'binding'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import bim_core
from promptbim.ai.nl_parser import NLParser, BIMIntent, IntentType
from promptbim.ai.intent_router import IntentRouter
from promptbim.ai.conversation_history import ConversationHistory
from promptbim.ai.error_handler import ErrorHandler

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


def setup_scene():
    sg = bim_core.BIMSceneGraph()
    bridge = bim_core.AgentBridge(sg)
    parser = NLParser(use_llm=False)
    router = IntentRouter()
    return sg, bridge, parser, router


def t01_create_wall():
    """T01: 建立一面牆 → NLParser → IntentRouter → bim_core.add"""
    print("T01: End-to-end create wall")
    sg, bridge, parser, router = setup_scene()

    intent = parser.parse("建立一面牆")
    check("NL→CREATE", intent.intent_type == IntentType.CREATE)
    check("entity=Wall", intent.entity_type == "Wall")
    check("is_valid", intent.is_valid)

    action = router.route(intent)
    check("route→add", action and action["action"] == "add")

    result = json.loads(bridge.execute_json(router.route_json(intent)))
    check("execute success", result["success"])
    check("entity_count=1", sg.entity_count() == 1)


def t02_modify_property():
    """T02: Modify entity property + query verification"""
    print("T02: Modify wall material + query")
    sg, bridge, parser, router = setup_scene()

    wall = bim_core.BIMEntity("wall-1", bim_core.EntityType.Wall, "Wall 1")
    wall.set_position(bim_core.Vec3(5, 5, 0))
    wall.set_dimensions(bim_core.Vec3(10, 0.3, 3))
    wall.set_property("material", "concrete")
    sg.add_entity(wall)

    check("material=concrete", wall.get_property("material") == "concrete")
    wall.set_property("material", "brick")
    check("material→brick", wall.get_property("material") == "brick")

    intent = parser.parse("查詢所有的牆")
    check("NL→QUERY_TYPE/Wall", intent.intent_type == IntentType.QUERY_TYPE and intent.entity_type == "Wall")
    result = json.loads(bridge.execute_json(router.route_json(intent)))
    check("query success", result["success"])


def t03_cost_calculation():
    """T03: 成本計算 → NL(COST) → bim_core.cost_delta"""
    print("T03: Cost calculation pipeline")
    sg, bridge, parser, router = setup_scene()

    for i, (eid, etype, ename) in enumerate([
        ("wall-1", bim_core.EntityType.Wall, "Wall 1"),
        ("chiller-1", bim_core.EntityType.Chiller, "Chiller 1"),
    ]):
        e = bim_core.BIMEntity(eid, etype, ename)
        e.set_dimensions(bim_core.Vec3(5, 3, 3))
        sg.add_entity(e)

    intent = parser.parse("成本是多少")
    check("NL→COST", intent.intent_type == IntentType.COST)
    result = json.loads(bridge.execute_json(router.route_json(intent)))
    check("cost_delta success", result["success"])

    info = json.loads(sg.scene_info())
    check("scene has 2 entities", info["entityCount"] == 2)
    check("Wall in distribution", "Wall" in info["typeDistribution"])
    check("Chiller in distribution", "Chiller" in info["typeDistribution"])


def t04_delete_entity():
    """T04: 刪除第三面牆 → delete action → SceneGraph更新"""
    print("T04: Delete wall-3")
    sg, bridge, parser, router = setup_scene()

    for i in range(1, 4):
        wall = bim_core.BIMEntity(f"wall-{i}", bim_core.EntityType.Wall, f"Wall {i}")
        wall.set_position(bim_core.Vec3(i * 5, 0, 0))
        sg.add_entity(wall)

    check("3 walls created", sg.entity_count() == 3)

    intent = parser.parse("刪除 wall-3")
    check("NL→DELETE", intent.intent_type == IntentType.DELETE)
    check("entity_id=wall-3", intent.entity_id == "wall-3")

    result = json.loads(bridge.execute_json(router.route_json(intent)))
    check("delete success", result["success"])
    check("entity_count=2", sg.entity_count() == 2)
    check("wall-3 gone", not sg.has_entity("wall-3"))
    check("wall-1 remains", sg.has_entity("wall-1"))


def t05_multi_turn():
    """T05: Multi-turn conversation with context preservation"""
    print("T05: Multi-turn conversation")
    sg, bridge, parser, router = setup_scene()
    history = ConversationHistory(system_message="BIM test assistant")

    commands = [
        ("建立一台冰水主機在 (10, 20, 0)", IntentType.CREATE),
        ("查詢所有的冰水主機", IntentType.QUERY_TYPE),
        ("成本是多少", IntentType.COST),
        ("場景概覽", IntentType.GET_SCENE_INFO),
    ]

    for text, expected_type in commands:
        history.add_user(text)
        intent = parser.parse(text)
        check(f"parse '{text[:10]}...'→{expected_type.value}", intent.intent_type == expected_type)
        result = json.loads(bridge.execute_json(router.route_json(intent)))
        check(f"execute '{text[:10]}...' success", result["success"])
        history.add_assistant(f"OK: {result.get('message', '')[:30]}")

    check("8 messages in history", history.message_count == 8)
    check("tokens > 0", history.estimated_tokens > 0)

    # Trimming test
    for i in range(30):
        history.add_user(f"msg {i}")
        history.add_assistant(f"rsp {i}")
    check("trimming works (<=20)", history.message_count <= 20)


def t06_error_handling():
    """T06: Error handling — invalid, nonexistent, low confidence"""
    print("T06: Error handling")
    sg, bridge, parser, router = setup_scene()
    eh = ErrorHandler()

    # Unknown command
    intent_bad = parser.parse("xyzzy gobbledygook")
    check("unknown→UNKNOWN", intent_bad.intent_type == IntentType.UNKNOWN)
    check("unknown not valid", not intent_bad.is_valid)
    msg = eh.handle_parse_failure("xyzzy")
    check("parse_failure has suggestions", "格式" in msg or "指令" in msg or "•" in msg)

    # Delete nonexistent
    intent_del = parser.parse("刪除 wall-999")
    result = json.loads(bridge.execute_json(router.route_json(intent_del)))
    check("delete nonexistent fails", not result["success"])

    # Execution error message
    err = eh.handle_execution_error(intent_del, "Entity not found: wall-999")
    check("exec error friendly", "找不到" in err or "ID" in err)

    # Low confidence
    low = BIMIntent(intent_type=IntentType.MOVE, confidence=0.35, raw_text="maybe")
    check("low_confidence msg", "信心度" in eh.handle_low_confidence(low) or "確定" in eh.handle_low_confidence(low))

    # Missing info
    missing = BIMIntent(intent_type=IntentType.CREATE, entity_type=None, position=None, raw_text="x")
    check("missing_info msg", "座標" in eh.handle_missing_info(missing) or "類型" in eh.handle_missing_info(missing))

    # Unknown routes to None
    check("UNKNOWN→None", router.route(intent_bad) is None)


def t07_stability_20ops():
    """T07: 20 consecutive operations without crash."""
    print("T07: 20 consecutive operations stability")
    sg, bridge, parser, router = setup_scene()

    operations = [
        "建立一面牆在 (0, 0, 0)", "建立一根柱子在 (5, 5, 0)",
        "建立一台冰水主機在 (10, 10, 0)", "查詢所有的牆", "場景概覽",
        "成本是多少", "建立一面牆在 (15, 0, 0)", "建立一根柱子在 (20, 5, 0)",
        "查詢所有的柱子", "建立一台泵在 (25, 10, 0)", "場景概覽",
        "成本是多少", "建立一面牆在 (30, 0, 0)", "查詢所有的冰水主機",
        "建立一根梁在 (35, 5, 0)", "建立一扇門在 (40, 0, 0)",
        "場景概覽", "成本是多少", "查詢所有的泵", "場景概覽",
    ]

    success = 0
    for i, cmd in enumerate(operations):
        try:
            intent = parser.parse(cmd)
            if intent.is_valid:
                r = json.loads(bridge.execute_json(router.route_json(intent)))
                if r.get("success"):
                    success += 1
        except Exception as e:
            check(f"op {i+1} no crash", False, str(e))
            return

    check(f"20/20 ops completed ({success} success)", success == 20)
    check(f"entities created", sg.entity_count() > 0)


def t08_memory_stability():
    """T08: RAM growth < 10% after 60 operations."""
    import resource
    print("T08: Memory stability")
    sg, bridge, parser, router = setup_scene()

    def rss_mb():
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)

    baseline = rss_mb()
    for i in range(20):
        for cmd in [f"建立一面牆在 ({i*5}, 0, 0)", "查詢所有的牆", "場景概覽"]:
            intent = parser.parse(cmd)
            if intent.is_valid:
                bridge.execute_json(router.route_json(intent))

    after = rss_mb()
    growth = ((after - baseline) / baseline * 100) if baseline > 0 else 0
    check(f"RAM growth {growth:.1f}% < 10%", growth < 10)


def t09_undo_rollback():
    """T09: Undo via JSON serialization/restore."""
    print("T09: Undo/rollback")
    sg, bridge, parser, router = setup_scene()

    wall = bim_core.BIMEntity("wall-1", bim_core.EntityType.Wall, "Wall 1")
    wall.set_position(bim_core.Vec3(5, 5, 0))
    wall.set_dimensions(bim_core.Vec3(10, 0.3, 3))
    sg.add_entity(wall)

    state_before = sg.to_json()
    bridge.execute_json(router.route_json(parser.parse("建立一根柱子在 (30, 30, 0)")))
    check("2 entities after add", sg.entity_count() == 2)

    sg2 = bim_core.BIMSceneGraph.from_json(state_before)
    check("rollback → 1 entity", sg2.entity_count() == 1)
    check("rollback has wall-1", sg2.has_entity("wall-1"))

    sg3 = bim_core.BIMSceneGraph.from_json(sg.to_json())
    check("JSON round-trip intact", sg3.entity_count() == 2)


def t10_offline_mode():
    """T10: Graceful behavior when Claude API unavailable."""
    print("T10: Offline / API unavailable")
    from promptbim.ai.claude_client import ClaudeClient

    parser_offline = NLParser(use_llm=False)
    intent = parser_offline.parse("建立一面牆")
    check("regex works offline", intent.intent_type == IntentType.CREATE)

    mock = ClaudeClient(mock_mode=True)
    r = mock.parse_intent("create a wall")
    check("mock parse works", r is not None and r.intent_type == IntentType.CREATE)

    chat_r = mock.chat([{"role": "user", "content": "hi"}])
    check("mock chat works", "mock" in chat_r.lower())

    eh = ErrorHandler()
    msg = eh.handle_parse_failure("ambiguous request")
    check("error handler offline", len(msg) > 10)


def t11_ctest_pass():
    """T11: ctest ALL PASS (verified externally, record here)."""
    print("T11: ctest verification")
    import subprocess
    r = subprocess.run(
        ["ctest", "--test-dir", "build", "--output-on-failure"],
        capture_output=True, text=True, timeout=60,
    )
    passed = "tests passed" in r.stdout and "0 tests failed" in r.stdout
    check("ctest ALL PASS", passed, r.stdout[-200:] if not passed else "")
    if passed:
        import re
        m = re.search(r"(\d+)/(\d+).*tests passed", r.stdout)
        if m:
            check(f"ctest {m.group(1)}/{m.group(2)}", True)


if __name__ == "__main__":
    print("=" * 60)
    print("S-PTB-INTEGRATION E2E Tests v2 — NL→AI→C++→Result")
    print("=" * 60)

    # Part 1: Integration (T01-T06)
    t01_create_wall()
    t02_modify_property()
    t03_cost_calculation()
    t04_delete_entity()
    t05_multi_turn()
    t06_error_handling()

    # Part 2: Stability (T07-T11)
    t07_stability_20ops()
    t08_memory_stability()
    t09_undo_rollback()
    t10_offline_mode()
    t11_ctest_pass()

    print("=" * 60)
    total = PASSED + FAILED
    print(f"Results: {PASSED}/{total} PASS, {FAILED} FAIL")
    if FAILED > 0:
        sys.exit(1)
    print("✅ ALL E2E INTEGRATION TESTS PASSED")
