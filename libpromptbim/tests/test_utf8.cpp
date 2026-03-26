/**
 * test_utf8.cpp — Verify UTF-8 Chinese messages in C++ engines
 *
 * Ensures that C++ JSON output contains valid UTF-8 Chinese characters
 * (P18 tech debt: CI locale confirmation).
 */

#include <gtest/gtest.h>
#include "promptbim/compliance_engine.hpp"
#include "promptbim/simulation_engine.hpp"
#include "promptbim/promptbim.h"

#include <string>

// -----------------------------------------------------------------------
// UTF-8 in Compliance Engine
// -----------------------------------------------------------------------

TEST(UTF8, ComplianceChineseMessages) {
    promptbim::ComplianceEngine engine;
    // Minimal valid plan
    std::string plan = R"({
        "stories": [{"name":"1F","height_m":3.0,"elevation_m":0,
                     "slab_boundary":[[0,0],[10,0],[10,10],[0,10]]}],
        "building_footprint": [[0,0],[10,0],[10,10],[0,10]]
    })";
    std::string land = R"({"area_sqm":200})";
    std::string zoning = R"({"bcr_limit":0.6,"far_limit":2.0,"height_limit_m":50})";

    std::string result = engine.check(plan, land, zoning);

    // Result should contain Chinese characters (UTF-8 multi-byte)
    // Check for common Chinese chars: 建蔽率 (BCR check)
    EXPECT_NE(result.find("\xe5\xbb\xba\xe8\x94\xbd\xe7\x8e\x87"), std::string::npos)
        << "Expected UTF-8 Chinese '建蔽率' in compliance result";

    // Also verify it's valid JSON
    auto j = nlohmann::json::parse(result);
    EXPECT_TRUE(j.contains("results"));
    EXPECT_GT(j["results"].size(), 0u);

    // Check that rule_name contains Chinese
    std::string rule_name = j["results"][0]["rule_name"].get<std::string>();
    EXPECT_FALSE(rule_name.empty());
    // Chinese characters are multi-byte; rule_name should be > 3 bytes
    EXPECT_GT(rule_name.size(), 3u);
}

// -----------------------------------------------------------------------
// UTF-8 in Simulation Engine
// -----------------------------------------------------------------------

TEST(UTF8, SimulationPhaseNames) {
    promptbim::SimulationEngine engine;
    std::vector<std::string> labels = {"Slab-1F", "Roof"};
    auto sched = engine.generate_schedule(labels, 360, 1);

    // Phase names are English in current impl, but verify JSON roundtrip
    auto j = sched.to_json();
    std::string json_str = j.dump();
    auto parsed = nlohmann::json::parse(json_str);
    EXPECT_TRUE(parsed.contains("phases"));
}

// -----------------------------------------------------------------------
// C ABI: pb_version returns valid UTF-8 string
// -----------------------------------------------------------------------

TEST(UTF8, VersionString) {
    const char* ver = pb_version();
    EXPECT_STREQ(ver, "2.7.0");
}
