/**
 * test_cost_engine.cpp — GoogleTest for the C++ Cost Engine.
 */

#include <gtest/gtest.h>
#include "promptbim/cost_engine.hpp"
#include "promptbim/promptbim.h"
#include <nlohmann/json.hpp>

static const char* PLAN_JSON = R"({
  "name": "TestProject",
  "building_footprint": [[0,0],[20,0],[20,15],[0,15]],
  "land_boundary": [[0,0],[30,0],[30,25],[0,25]],
  "stories": [
    {
      "name": "F1",
      "elevation_m": 0, "height_m": 3.5, "slab_thickness_m": 0.2,
      "slab_boundary": [[0,0],[20,0],[20,15],[0,15]],
      "walls": [
        {"start":[0,0],"end":[20,0],"wall_type":"exterior","thickness_m":0.2},
        {"start":[0,15],"end":[20,15],"wall_type":"exterior","thickness_m":0.2},
        {"start":[0,0],"end":[0,15],"wall_type":"exterior","thickness_m":0.2},
        {"start":[20,0],"end":[20,15],"wall_type":"exterior","thickness_m":0.2}
      ],
      "openings": [
        {"opening_type":"door","width_m":0.9,"height_m":2.1},
        {"opening_type":"window","width_m":1.8,"height_m":1.2},
        {"opening_type":"window","width_m":1.8,"height_m":1.2}
      ],
      "spaces": []
    },
    {
      "name": "F2",
      "elevation_m": 3.5, "height_m": 3.5, "slab_thickness_m": 0.2,
      "slab_boundary": [[0,0],[20,0],[20,15],[0,15]],
      "walls": [
        {"start":[0,0],"end":[20,0],"wall_type":"interior","thickness_m":0.1}
      ],
      "openings": [],
      "spaces": []
    }
  ]
})";

class CostEngineTest : public ::testing::Test {
protected:
    promptbim::CostEngine engine;
};

TEST_F(CostEngineTest, ReturnsValidJSON) {
    std::string result = engine.estimate(PLAN_JSON);
    // Should parse without exception
    auto j = nlohmann::json::parse(result);
    EXPECT_TRUE(j.contains("project"));
    EXPECT_TRUE(j.contains("total_cost_twd"));
    EXPECT_TRUE(j.contains("total_floor_area_sqm"));
    EXPECT_TRUE(j.contains("cost_per_sqm_twd"));
    EXPECT_TRUE(j.contains("breakdown"));
    EXPECT_TRUE(j.contains("notes"));
}

TEST_F(CostEngineTest, PositiveTotalCost) {
    std::string result = engine.estimate(PLAN_JSON);
    auto j = nlohmann::json::parse(result);
    EXPECT_GT(j["total_cost_twd"].get<long long>(), 0LL);
}

TEST_F(CostEngineTest, FloorAreaIsCorrect) {
    // 2 stories × 300 sqm = 600 sqm total floor area
    std::string result = engine.estimate(PLAN_JSON);
    auto j = nlohmann::json::parse(result);
    double fa = j["total_floor_area_sqm"].get<double>();
    EXPECT_NEAR(fa, 600.0, 1.0);
}

TEST_F(CostEngineTest, CostPerSqmIsReasonable) {
    // Taiwan 2025 construction cost: 30,000 – 100,000 TWD/sqm (POC estimate)
    std::string result = engine.estimate(PLAN_JSON);
    auto j = nlohmann::json::parse(result);
    long long cpp_sqm = j["cost_per_sqm_twd"].get<long long>();
    EXPECT_GT(cpp_sqm, 5000LL)   << "Cost per sqm too low";
    EXPECT_LT(cpp_sqm, 500000LL) << "Cost per sqm unreasonably high";
}

TEST_F(CostEngineTest, BreakdownRatiosSumToOne) {
    std::string result = engine.estimate(PLAN_JSON);
    auto j = nlohmann::json::parse(result);
    double total_ratio = 0.0;
    for (const auto& b : j["breakdown"]) {
        total_ratio += b["ratio"].get<double>();
    }
    EXPECT_NEAR(total_ratio, 1.0, 0.05);  // Allow 5% rounding error
}

TEST_F(CostEngineTest, ProjectNamePreserved) {
    std::string result = engine.estimate(PLAN_JSON);
    auto j = nlohmann::json::parse(result);
    EXPECT_EQ(j["project"].get<std::string>(), "TestProject");
}

TEST_F(CostEngineTest, EmptyPlanReturnsSafeResult) {
    std::string empty_plan = R"({"name":"Empty","stories":[]})";
    std::string result = engine.estimate(empty_plan);
    auto j = nlohmann::json::parse(result);
    EXPECT_EQ(j["total_cost_twd"].get<long long>(), 0LL);
    EXPECT_EQ(j["total_floor_area_sqm"].get<double>(), 0.0);
}

TEST_F(CostEngineTest, InvalidJsonReturnsError) {
    std::string result = engine.estimate("not json");
    auto j = nlohmann::json::parse(result);
    EXPECT_TRUE(j.contains("error"));
}

// ---------------------------------------------------------------------------
// C ABI tests
// ---------------------------------------------------------------------------

TEST(CostCABI, ReturnsValidJSON) {
    char* out = pb_estimate_cost(PLAN_JSON);
    ASSERT_NE(out, nullptr);
    auto j = nlohmann::json::parse(std::string(out));
    EXPECT_TRUE(j.contains("total_cost_twd"));
    pb_free_string(out);
}

TEST(CostCABI, NullInputReturnsNull) {
    EXPECT_EQ(pb_estimate_cost(nullptr), nullptr);
}
