// PromptBIM C++ Tests — Cost Engine
#include <gtest/gtest.h>
#include "cost_engine.h"

using namespace promptbim;

class CostEngineTest : public ::testing::Test {
protected:
    CostEngine engine;
};

TEST_F(CostEngineTest, ResidentialRC) {
    BuildingParams params;
    params.total_floor_area_sqm = 450.0;
    params.num_stories = 3;
    params.building_type = "residential";
    params.structure_type = "rc";
    params.quality_level = 3;

    auto result = engine.estimate(params);
    EXPECT_GT(result.total_cost, 0.0);
    EXPECT_GT(result.cost_per_sqm, 0.0);
    EXPECT_EQ(result.currency, "NTD");
    // Sum check
    double sum = result.structure_cost + result.exterior_cost
               + result.interior_cost + result.mep_cost;
    EXPECT_NEAR(result.total_cost, sum, 0.01);
}

TEST_F(CostEngineTest, SteelMoreExpensive) {
    BuildingParams rc_params;
    rc_params.total_floor_area_sqm = 300.0;
    rc_params.structure_type = "rc";
    rc_params.quality_level = 3;

    BuildingParams steel_params = rc_params;
    steel_params.structure_type = "steel";

    auto rc_cost = engine.estimate(rc_params);
    auto steel_cost = engine.estimate(steel_params);
    EXPECT_GT(steel_cost.total_cost, rc_cost.total_cost);
}

TEST_F(CostEngineTest, QualityScaling) {
    BuildingParams base;
    base.total_floor_area_sqm = 300.0;
    base.quality_level = 1;
    auto low = engine.estimate(base);

    base.quality_level = 5;
    auto high = engine.estimate(base);

    EXPECT_GT(high.total_cost, low.total_cost);
}

TEST_F(CostEngineTest, HeightPremium) {
    BuildingParams low_rise;
    low_rise.total_floor_area_sqm = 1000.0;
    low_rise.num_stories = 3;
    auto cost3 = engine.estimate(low_rise);

    low_rise.num_stories = 10;
    auto cost10 = engine.estimate(low_rise);

    EXPECT_GT(cost10.cost_per_sqm, cost3.cost_per_sqm);
}

TEST_F(CostEngineTest, ZeroArea) {
    BuildingParams params;
    params.total_floor_area_sqm = 0.0;
    auto result = engine.estimate(params);
    EXPECT_DOUBLE_EQ(result.total_cost, 0.0);
    EXPECT_DOUBLE_EQ(result.cost_per_sqm, 0.0);
}

TEST_F(CostEngineTest, Version) {
    EXPECT_EQ(CostEngine::version(), "3.0.0");
}
