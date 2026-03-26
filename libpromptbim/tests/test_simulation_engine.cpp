/**
 * test_simulation_engine.cpp — GoogleTest for 4D Construction Simulation Engine
 *
 * Covers: schedule generation, component classification, phase sequencing,
 *         story scaling, visibility states, active phase queries.
 */

#include <gtest/gtest.h>
#include "promptbim/simulation_engine.hpp"

using namespace promptbim;

// -----------------------------------------------------------------------
// Component classification
// -----------------------------------------------------------------------

TEST(SimulationEngine, ClassifyRoof) {
    SimulationEngine engine;
    EXPECT_EQ(engine.classify_component("Roof"), "P08");
}

TEST(SimulationEngine, ClassifySlab) {
    SimulationEngine engine;
    EXPECT_EQ(engine.classify_component("Slab-1F"), "P06");
}

TEST(SimulationEngine, ClassifyGroundSlab) {
    SimulationEngine engine;
    EXPECT_EQ(engine.classify_component("ground_slab"), "P02");
}

TEST(SimulationEngine, ClassifyExteriorWall) {
    SimulationEngine engine;
    EXPECT_EQ(engine.classify_component("Wall-exterior-1F-0"), "P09");
}

TEST(SimulationEngine, ClassifyPartitionWall) {
    SimulationEngine engine;
    EXPECT_EQ(engine.classify_component("Wall-partition-1F-0"), "P12");
    EXPECT_EQ(engine.classify_component("Wall-interior-2F"), "P12");
}

TEST(SimulationEngine, ClassifyDoorWindow) {
    SimulationEngine engine;
    EXPECT_EQ(engine.classify_component("door-1F-0"), "P10");
    EXPECT_EQ(engine.classify_component("Window-2F"), "P10");
}

TEST(SimulationEngine, ClassifyMEP) {
    SimulationEngine engine;
    EXPECT_EQ(engine.classify_component("duct-HVAC"), "P11");
    EXPECT_EQ(engine.classify_component("PipeSegment"), "P11");
    EXPECT_EQ(engine.classify_component("CableCarrier"), "P11");
}

TEST(SimulationEngine, ClassifyUnknown) {
    SimulationEngine engine;
    EXPECT_FALSE(engine.classify_component("unknown_thing").has_value());
}

TEST(SimulationEngine, ClassifyColumn) {
    SimulationEngine engine;
    EXPECT_EQ(engine.classify_component("Column-1F"), "P04");
}

TEST(SimulationEngine, ClassifyBeam) {
    SimulationEngine engine;
    EXPECT_EQ(engine.classify_component("Beam-2F"), "P05");
}

// -----------------------------------------------------------------------
// Schedule generation
// -----------------------------------------------------------------------

TEST(SimulationEngine, GenerateScheduleBasic) {
    SimulationEngine engine;
    std::vector<std::string> labels = {
        "Slab-1F", "Wall-exterior-1F-0", "Roof",
        "door-1F-0", "Column-1F", "Beam-1F",
    };
    auto sched = engine.generate_schedule(labels, 360, 1);
    EXPECT_GT(sched.phases.size(), 3u);
    EXPECT_GT(sched.total_days, 0);
}

TEST(SimulationEngine, PhasesSequential) {
    SimulationEngine engine;
    std::vector<std::string> labels = {
        "Slab-1F", "Wall-exterior-1F-0", "Roof", "Column-1F",
    };
    auto sched = engine.generate_schedule(labels, 360, 1);

    for (size_t i = 1; i < sched.phases.size(); ++i) {
        EXPECT_GE(sched.phases[i].start_day, sched.phases[i - 1].end_day);
    }
}

TEST(SimulationEngine, NoPhaseOverlap) {
    SimulationEngine engine;
    std::vector<std::string> labels = {
        "Slab-1F", "Wall-exterior-1F-0", "Roof", "door-1F-0",
    };
    auto sched = engine.generate_schedule(labels, 360, 1);

    for (size_t i = 1; i < sched.phases.size(); ++i) {
        EXPECT_LE(sched.phases[i - 1].end_day, sched.phases[i].start_day);
    }
}

TEST(SimulationEngine, StoryScaling) {
    SimulationEngine engine;
    std::vector<std::string> labels = {"Slab-1F", "Wall-exterior-1F-0"};

    auto sched1 = engine.generate_schedule(labels, 360, 1);
    auto sched6 = engine.generate_schedule(labels, 360, 6);

    EXPECT_GT(sched6.total_days, sched1.total_days);
}

TEST(SimulationEngine, SitePrepAlwaysIncluded) {
    SimulationEngine engine;
    std::vector<std::string> labels = {"Slab-1F"};
    auto sched = engine.generate_schedule(labels, 360, 1);

    bool has_p01 = false;
    for (const auto& p : sched.phases) {
        if (p.phase_id == "P01") has_p01 = true;
    }
    EXPECT_TRUE(has_p01);
}

// -----------------------------------------------------------------------
// Visibility states
// -----------------------------------------------------------------------

TEST(SimulationEngine, VisibilityHidden) {
    SimulationEngine engine;
    std::vector<std::string> labels = {"Slab-1F", "Roof"};
    auto sched = engine.generate_schedule(labels, 360, 1);

    // At day 0, later phases should be hidden
    auto vis = engine.get_visible_components(sched, 0);
    // P01 (site prep) is at day 0, so components of later phases are hidden
    for (const auto& [comp, state] : vis) {
        // At least some should be hidden or in_progress at day 0
        EXPECT_TRUE(state == VisibilityState::HIDDEN ||
                    state == VisibilityState::IN_PROGRESS);
    }
}

TEST(SimulationEngine, VisibilityCompleted) {
    SimulationEngine engine;
    std::vector<std::string> labels = {"Slab-1F"};
    auto sched = engine.generate_schedule(labels, 360, 1);

    // At the very end, everything should be completed
    auto vis = engine.get_visible_components(sched, sched.total_days + 1);
    for (const auto& [comp, state] : vis) {
        EXPECT_EQ(state, VisibilityState::COMPLETED);
    }
}

// -----------------------------------------------------------------------
// Active phase
// -----------------------------------------------------------------------

TEST(SimulationEngine, ActivePhase) {
    SimulationEngine engine;
    std::vector<std::string> labels = {"Slab-1F", "Column-1F", "Roof"};
    auto sched = engine.generate_schedule(labels, 360, 1);

    // At day 0, should have an active phase (P01 site prep)
    auto active = engine.get_active_phase(sched, 0);
    EXPECT_TRUE(active.has_value());
}

TEST(SimulationEngine, ActivePhaseNone) {
    SimulationEngine engine;
    std::vector<std::string> labels = {"Slab-1F"};
    auto sched = engine.generate_schedule(labels, 360, 1);

    // Way past the end, no active phase
    auto active = engine.get_active_phase(sched, 99999);
    EXPECT_FALSE(active.has_value());
}

// -----------------------------------------------------------------------
// JSON interface
// -----------------------------------------------------------------------

TEST(SimulationEngine, GenerateScheduleJSON) {
    SimulationEngine engine;
    nlohmann::json plan = {
        {"building_footprint", {{0,0}, {10,0}, {10,8}, {0,8}}},
        {"stories", {{
            {"name", "1F"},
            {"elevation_m", 0.0},
            {"height_m", 3.0},
            {"slab_boundary", {{0,0}, {10,0}, {10,8}, {0,8}}},
            {"walls", {{
                {"start", {0, 0}}, {"end", {10, 0}}, {"wall_type", "exterior"}
            }}},
            {"openings", {{
                {"opening_type", "door"}
            }}},
        }}},
    };
    std::string result = engine.generate_schedule_json(plan.dump(), 360);
    auto j = nlohmann::json::parse(result);
    EXPECT_TRUE(j.contains("phases"));
    EXPECT_TRUE(j.contains("total_days"));
}

TEST(SimulationEngine, GenerateScheduleInvalidJSON) {
    SimulationEngine engine;
    std::string result = engine.generate_schedule_json("bad-json", 360);
    auto j = nlohmann::json::parse(result);
    EXPECT_TRUE(j.contains("error"));
}
