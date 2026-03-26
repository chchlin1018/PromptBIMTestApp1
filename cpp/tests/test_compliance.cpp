// PromptBIM C++ Tests — Compliance Engine
#include <gtest/gtest.h>
#include "compliance_engine.h"

using namespace promptbim;

class ComplianceEngineTest : public ::testing::Test {
protected:
    ComplianceEngine engine;
    ZoningParams residential;

    void SetUp() override {
        residential.zone_type = "residential";
        residential.bcr_limit = 0.6;
        residential.far_limit = 2.0;
        residential.height_limit_m = 15.0;
    }
};

TEST_F(ComplianceEngineTest, PassingPlan) {
    auto result = engine.check(500.0, 250.0, 750.0, 12.0, residential);
    EXPECT_TRUE(result.passed);
    EXPECT_DOUBLE_EQ(result.bcr, 0.5);
    EXPECT_DOUBLE_EQ(result.far_ratio, 1.5);
    EXPECT_TRUE(result.violations.empty());
}

TEST_F(ComplianceEngineTest, BcrExceeded) {
    auto result = engine.check(500.0, 350.0, 750.0, 12.0, residential);
    EXPECT_FALSE(result.passed);
    EXPECT_EQ(result.violations.size(), 1);
    EXPECT_NE(result.violations[0].find("BCR"), std::string::npos);
}

TEST_F(ComplianceEngineTest, FarExceeded) {
    auto result = engine.check(500.0, 250.0, 1200.0, 12.0, residential);
    EXPECT_FALSE(result.passed);
    EXPECT_EQ(result.violations.size(), 1);
    EXPECT_NE(result.violations[0].find("FAR"), std::string::npos);
}

TEST_F(ComplianceEngineTest, HeightExceeded) {
    auto result = engine.check(500.0, 250.0, 750.0, 20.0, residential);
    EXPECT_FALSE(result.passed);
    EXPECT_NE(result.violations[0].find("Height"), std::string::npos);
}

TEST_F(ComplianceEngineTest, MultipleViolations) {
    auto result = engine.check(500.0, 400.0, 1500.0, 20.0, residential);
    EXPECT_FALSE(result.passed);
    EXPECT_EQ(result.violations.size(), 3);
}

TEST_F(ComplianceEngineTest, NearLimitWarning) {
    // BCR = 0.56 (93% of 0.6 limit)
    auto result = engine.check(500.0, 280.0, 750.0, 12.0, residential);
    EXPECT_TRUE(result.passed);
    EXPECT_FALSE(result.warnings.empty());
}

TEST_F(ComplianceEngineTest, ZeroLandArea) {
    auto result = engine.check(0.0, 250.0, 750.0, 12.0, residential);
    EXPECT_DOUBLE_EQ(result.bcr, 0.0);
    EXPECT_DOUBLE_EQ(result.far_ratio, 0.0);
}

TEST_F(ComplianceEngineTest, Version) {
    EXPECT_EQ(ComplianceEngine::version(), "3.0.0");
}
