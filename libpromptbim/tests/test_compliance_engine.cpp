/**
 * test_compliance_engine.cpp — GoogleTest for the C++ Compliance Engine.
 *
 * Test fixtures mirror the Python tests in tests/test_compliance*.py.
 */

#include <gtest/gtest.h>
#include "promptbim/compliance_engine.hpp"
#include "promptbim/promptbim.h"
#include <nlohmann/json.hpp>
#include <cstring>

// ---------------------------------------------------------------------------
// Shared fixtures
// ---------------------------------------------------------------------------

// A simple 2-story building that PASSES most rules
static const char* PLAN_PASS_JSON = R"({
  "name": "TestBuilding",
  "building_footprint": [[0,0],[20,0],[20,15],[0,15]],
  "land_boundary": [[0,0],[30,0],[30,25],[0,25]],
  "stories": [
    {
      "name": "F1",
      "elevation_m": 0,
      "height_m": 3.5,
      "slab_thickness_m": 0.2,
      "slab_boundary": [[0,0],[20,0],[20,15],[0,15]],
      "walls": [
        {"start":[0,0],"end":[20,0],"wall_type":"exterior","thickness_m":0.2},
        {"start":[0,0],"end":[0,15],"wall_type":"exterior","thickness_m":0.2}
      ],
      "openings": [
        {"opening_type":"door","width_m":0.9,"height_m":2.1},
        {"opening_type":"window","width_m":1.8,"height_m":1.2}
      ],
      "spaces": []
    },
    {
      "name": "F2",
      "elevation_m": 3.5,
      "height_m": 3.5,
      "slab_thickness_m": 0.2,
      "slab_boundary": [[0,0],[20,0],[20,15],[0,15]],
      "walls": [
        {"start":[0,0],"end":[20,0],"wall_type":"exterior","thickness_m":0.2}
      ],
      "openings": [],
      "spaces": []
    }
  ],
  "parking_spaces": 6
})";

// A building that FAILS BCR (footprint covers 90% of land)
static const char* PLAN_FAIL_BCR_JSON = R"({
  "name": "OverBCR",
  "building_footprint": [[0,0],[27,0],[27,23],[0,23]],
  "land_boundary": [[0,0],[30,0],[30,25],[0,25]],
  "stories": [
    {
      "name": "F1",
      "elevation_m": 0, "height_m": 3.5, "slab_thickness_m": 0.2,
      "slab_boundary": [[0,0],[27,0],[27,23],[0,23]],
      "walls": [], "openings": [], "spaces": []
    }
  ]
})";

// A building that FAILS FAR (10 stories, each 300 sqm on 300 sqm land)
static const char* PLAN_FAIL_FAR_JSON = R"({
  "name": "OverFAR",
  "building_footprint": [[0,0],[20,0],[20,15],[0,15]],
  "land_boundary": [[0,0],[20,0],[20,15],[0,15]],
  "stories": [
    {"name":"F1","elevation_m":0,"height_m":3.5,"slab_thickness_m":0.2,
     "slab_boundary":[[0,0],[20,0],[20,15],[0,15]],"walls":[],"openings":[],"spaces":[]},
    {"name":"F2","elevation_m":3.5,"height_m":3.5,"slab_thickness_m":0.2,
     "slab_boundary":[[0,0],[20,0],[20,15],[0,15]],"walls":[],"openings":[],"spaces":[]},
    {"name":"F3","elevation_m":7.0,"height_m":3.5,"slab_thickness_m":0.2,
     "slab_boundary":[[0,0],[20,0],[20,15],[0,15]],"walls":[],"openings":[],"spaces":[]},
    {"name":"F4","elevation_m":10.5,"height_m":3.5,"slab_thickness_m":0.2,
     "slab_boundary":[[0,0],[20,0],[20,15],[0,15]],"walls":[],"openings":[],"spaces":[]},
    {"name":"F5","elevation_m":14.0,"height_m":3.5,"slab_thickness_m":0.2,
     "slab_boundary":[[0,0],[20,0],[20,15],[0,15]],"walls":[],"openings":[],"spaces":[]},
    {"name":"F6","elevation_m":17.5,"height_m":3.5,"slab_thickness_m":0.2,
     "slab_boundary":[[0,0],[20,0],[20,15],[0,15]],"walls":[],"openings":[],"spaces":[]}
  ]
})";

static const char* LAND_JSON = R"({"area_sqm": 750.0})";
static const char* ZONING_JSON = R"({
  "bcr_limit": 0.6,
  "far_limit": 2.0,
  "height_limit_m": 21.0
})";

// ---------------------------------------------------------------------------
// C++ API tests
// ---------------------------------------------------------------------------

class ComplianceEngineTest : public ::testing::Test {
protected:
    promptbim::ComplianceEngine engine;
};

TEST_F(ComplianceEngineTest, PassingBuildingHasNoFails) {
    std::string result = engine.check(PLAN_PASS_JSON, LAND_JSON, ZONING_JSON);
    auto j = nlohmann::json::parse(result);
    EXPECT_EQ(j["failed"].get<int>(), 0);
    EXPECT_GE(j["passed"].get<int>(), 1);
}

TEST_F(ComplianceEngineTest, OverBCRFails) {
    std::string result = engine.check(PLAN_FAIL_BCR_JSON, LAND_JSON, ZONING_JSON);
    auto j = nlohmann::json::parse(result);

    bool found_bcr_fail = false;
    for (const auto& r : j["results"]) {
        if (r["rule_id"] == "TW-BTC-BCR" && r["severity"] == "fail")
            found_bcr_fail = true;
    }
    EXPECT_TRUE(found_bcr_fail) << "Expected BCR rule to FAIL";
}

TEST_F(ComplianceEngineTest, OverFARFails) {
    // 6 stories * 300 sqm = 1800 sqm on 300 sqm land → FAR = 6.0 > 2.0
    std::string result = engine.check(PLAN_FAIL_FAR_JSON, LAND_JSON, ZONING_JSON);
    auto j = nlohmann::json::parse(result);

    bool found_far_fail = false;
    for (const auto& r : j["results"]) {
        if (r["rule_id"] == "TW-BTC-FAR" && r["severity"] == "fail")
            found_far_fail = true;
    }
    EXPECT_TRUE(found_far_fail) << "Expected FAR rule to FAIL";
}

TEST_F(ComplianceEngineTest, HeightOverLimitFails) {
    // Build a plan with height 25m but limit 21m
    std::string plan_json = R"({
      "name": "TallBuilding",
      "building_footprint": [[0,0],[10,0],[10,10],[0,10]],
      "land_boundary": [[0,0],[20,0],[20,20],[0,20]],
      "stories": [
        {"name":"F1","elevation_m":0,"height_m":4.0,"slab_thickness_m":0.2,
         "slab_boundary":[[0,0],[10,0],[10,10],[0,10]],"walls":[],"openings":[],"spaces":[]},
        {"name":"F2","elevation_m":4.0,"height_m":4.0,"slab_thickness_m":0.2,
         "slab_boundary":[[0,0],[10,0],[10,10],[0,10]],"walls":[],"openings":[],"spaces":[]},
        {"name":"F3","elevation_m":8.0,"height_m":4.0,"slab_thickness_m":0.2,
         "slab_boundary":[[0,0],[10,0],[10,10],[0,10]],"walls":[],"openings":[],"spaces":[]},
        {"name":"F4","elevation_m":12.0,"height_m":4.0,"slab_thickness_m":0.2,
         "slab_boundary":[[0,0],[10,0],[10,10],[0,10]],"walls":[],"openings":[],"spaces":[]},
        {"name":"F5","elevation_m":16.0,"height_m":5.5,"slab_thickness_m":0.2,
         "slab_boundary":[[0,0],[10,0],[10,10],[0,10]],"walls":[],"openings":[],"spaces":[]}
      ]
    })";
    std::string result = engine.check(plan_json, LAND_JSON, ZONING_JSON);
    auto j = nlohmann::json::parse(result);

    bool found_height_fail = false;
    for (const auto& r : j["results"]) {
        if (r["rule_id"] == "TW-BTC-24-1" && r["severity"] == "fail")
            found_height_fail = true;
    }
    EXPECT_TRUE(found_height_fail) << "Expected height rule to FAIL (21.5m > 21m limit)";
}

TEST_F(ComplianceEngineTest, ResultHasAllExpectedFields) {
    std::string result = engine.check(PLAN_PASS_JSON, LAND_JSON, ZONING_JSON);
    auto j = nlohmann::json::parse(result);

    EXPECT_TRUE(j.contains("total_rules"));
    EXPECT_TRUE(j.contains("passed"));
    EXPECT_TRUE(j.contains("warnings"));
    EXPECT_TRUE(j.contains("failed"));
    EXPECT_TRUE(j.contains("info"));
    EXPECT_TRUE(j.contains("compliance_rate"));
    EXPECT_TRUE(j.contains("results"));
    EXPECT_EQ(j["total_rules"].get<int>(), 15);
}

TEST_F(ComplianceEngineTest, AllResultsHaveRuleIdAndSeverity) {
    std::string result = engine.check(PLAN_PASS_JSON, LAND_JSON, ZONING_JSON);
    auto j = nlohmann::json::parse(result);

    for (const auto& r : j["results"]) {
        EXPECT_TRUE(r.contains("rule_id"))   << "Missing rule_id";
        EXPECT_TRUE(r.contains("severity"))  << "Missing severity";
        EXPECT_TRUE(r.contains("rule_name")) << "Missing rule_name";

        std::string sev = r["severity"].get<std::string>();
        bool valid_sev = (sev == "pass" || sev == "warning" || sev == "fail" || sev == "info");
        EXPECT_TRUE(valid_sev) << "Invalid severity: " << sev;
    }
}

TEST_F(ComplianceEngineTest, ZeroLandAreaReturnsInfo) {
    std::string land_zero = R"({"area_sqm": 0})";
    std::string result = engine.check(PLAN_PASS_JSON, land_zero, ZONING_JSON);
    auto j = nlohmann::json::parse(result);

    bool found_info = false;
    for (const auto& r : j["results"]) {
        if (r["rule_id"] == "TW-BTC-BCR" && r["severity"] == "info")
            found_info = true;
    }
    EXPECT_TRUE(found_info);
}

TEST_F(ComplianceEngineTest, InvalidJsonReturnsErrorObject) {
    std::string result = engine.check("not json", "{}", "{}");
    auto j = nlohmann::json::parse(result);
    EXPECT_TRUE(j.contains("error"));
}

// ---------------------------------------------------------------------------
// C ABI tests
// ---------------------------------------------------------------------------

TEST(ComplianceCABI, ReturnsValidJSON) {
    char* out = pb_check_compliance(PLAN_PASS_JSON, LAND_JSON, ZONING_JSON);
    ASSERT_NE(out, nullptr);

    auto j = nlohmann::json::parse(std::string(out));
    EXPECT_TRUE(j.contains("total_rules"));
    pb_free_string(out);
}

TEST(ComplianceCABI, FreedStringWasAllocated) {
    char* out = pb_check_compliance(PLAN_PASS_JSON, LAND_JSON, ZONING_JSON);
    ASSERT_NE(out, nullptr);
    // Must not crash
    pb_free_string(out);
}
