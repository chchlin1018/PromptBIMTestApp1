/**
 * test_version.cpp — Basic sanity tests for C ABI and version string.
 */

#include <gtest/gtest.h>
#include "promptbim/promptbim.h"
#include <cstring>

TEST(Version, VersionString) {
    const char* v = pb_version();
    ASSERT_NE(v, nullptr);
    EXPECT_STREQ(v, "2.5.0");
}

TEST(Memory, FreeNullIsNoop) {
    // Should not crash
    pb_free_string(nullptr);
}

TEST(ComplianceABI, NullInputReturnsNull) {
    EXPECT_EQ(pb_check_compliance(nullptr, nullptr, nullptr), nullptr);
    EXPECT_EQ(pb_check_compliance("{}", nullptr, nullptr), nullptr);
}

TEST(CostABI, NullInputReturnsNull) {
    EXPECT_EQ(pb_estimate_cost(nullptr), nullptr);
}
