/**
 * test_version.cpp — Sanity tests for C ABI, version string, concurrency,
 * edge cases, ABI stability, memory safety, and plan lifecycle.
 *
 * P23: expanded from 4 to 17 tests.
 */

#include <gtest/gtest.h>
#include "promptbim/promptbim.h"
#include <cstring>
#include <atomic>
#include <string>
#include <thread>
#include <vector>

// =========================================================================
// Original tests (4)
// =========================================================================

TEST(Version, VersionString) {
    const char* v = pb_version();
    ASSERT_NE(v, nullptr);
    EXPECT_STREQ(v, "2.11.0");
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

// =========================================================================
// P23: Concurrency tests — version call from multiple threads (3 tests)
// =========================================================================

TEST(Concurrency, VersionFromMultipleThreads) {
    constexpr int NUM_THREADS = 8;
    std::atomic<int> success{0};
    std::vector<std::thread> threads;

    for (int i = 0; i < NUM_THREADS; ++i) {
        threads.emplace_back([&]() {
            const char* v = pb_version();
            if (v != nullptr && std::strcmp(v, "2.11.0") == 0) {
                success++;
            }
        });
    }
    for (auto& t : threads) t.join();
    EXPECT_EQ(success.load(), NUM_THREADS);
}

TEST(Concurrency, CostNullFromMultipleThreads) {
    constexpr int NUM_THREADS = 4;
    std::atomic<int> null_count{0};
    std::vector<std::thread> threads;

    for (int i = 0; i < NUM_THREADS; ++i) {
        threads.emplace_back([&]() {
            char* result = pb_estimate_cost(nullptr);
            if (result == nullptr) null_count++;
        });
    }
    for (auto& t : threads) t.join();
    EXPECT_EQ(null_count.load(), NUM_THREADS);
}

TEST(Concurrency, ComplianceNullFromMultipleThreads) {
    constexpr int NUM_THREADS = 4;
    std::atomic<int> null_count{0};
    std::vector<std::thread> threads;

    for (int i = 0; i < NUM_THREADS; ++i) {
        threads.emplace_back([&]() {
            char* result = pb_check_compliance(nullptr, nullptr, nullptr);
            if (result == nullptr) null_count++;
        });
    }
    for (auto& t : threads) t.join();
    EXPECT_EQ(null_count.load(), NUM_THREADS);
}

// =========================================================================
// P23: Edge case tests — empty strings, null handling (3 tests)
// =========================================================================

TEST(EdgeCase, ComplianceEmptyStrings) {
    // Empty strings (not null) — should return null or valid JSON, not crash
    char* result = pb_check_compliance("", "", "");
    // Implementation may return null for unparseable input
    if (result) pb_free_string(result);
}

TEST(EdgeCase, CostEmptyString) {
    char* result = pb_estimate_cost("");
    if (result) pb_free_string(result);
}

TEST(EdgeCase, PlanFromEmptyString) {
    PBPlan* plan = pb_plan_from_json("");
    // Should return null for empty/invalid JSON
    EXPECT_EQ(plan, nullptr);
}

// =========================================================================
// P23: ABI stability tests — function signatures exist (2 tests)
// =========================================================================

TEST(ABIStability, AllCABIFunctionsExist) {
    // Verify function pointers are non-null (they exist in the binary)
    EXPECT_NE(reinterpret_cast<void*>(&pb_version), nullptr);
    EXPECT_NE(reinterpret_cast<void*>(&pb_free_string), nullptr);
    EXPECT_NE(reinterpret_cast<void*>(&pb_check_compliance), nullptr);
    EXPECT_NE(reinterpret_cast<void*>(&pb_estimate_cost), nullptr);
    EXPECT_NE(reinterpret_cast<void*>(&pb_plan_from_json), nullptr);
    EXPECT_NE(reinterpret_cast<void*>(&pb_plan_free), nullptr);
    EXPECT_NE(reinterpret_cast<void*>(&pb_plan_to_json), nullptr);
    EXPECT_NE(reinterpret_cast<void*>(&pb_generate_ifc), nullptr);
    EXPECT_NE(reinterpret_cast<void*>(&pb_generate_usd), nullptr);
    EXPECT_NE(reinterpret_cast<void*>(&pb_generate_usdz), nullptr);
}

TEST(ABIStability, VersionStringIsStatic) {
    // pb_version() should return the same pointer every time
    // (it returns a static string literal, not a heap allocation)
    const char* v1 = pb_version();
    const char* v2 = pb_version();
    EXPECT_EQ(v1, v2);  // same pointer
}

// =========================================================================
// P23: Memory tests — double-free safety (2 tests)
// =========================================================================

TEST(Memory, DoubleFreeNullSafe) {
    // Calling pb_free_string(nullptr) twice should be safe
    pb_free_string(nullptr);
    pb_free_string(nullptr);
}

TEST(Memory, PlanFreeNullSafe) {
    // Calling pb_plan_free(nullptr) should not crash
    pb_plan_free(nullptr);
    pb_plan_free(nullptr);
}

// =========================================================================
// P23: Plan lifecycle tests — from_json with invalid input (3 tests)
// =========================================================================

TEST(PlanLifecycle, InvalidJsonReturnNull) {
    PBPlan* plan = pb_plan_from_json("{bad json");
    EXPECT_EQ(plan, nullptr);
}

TEST(PlanLifecycle, NullJsonReturnNull) {
    PBPlan* plan = pb_plan_from_json(nullptr);
    EXPECT_EQ(plan, nullptr);
}

TEST(PlanLifecycle, ValidMinimalJson) {
    const char* json = R"({"name": "Minimal", "stories": []})";
    PBPlan* plan = pb_plan_from_json(json);
    ASSERT_NE(plan, nullptr);

    char* out = pb_plan_to_json(plan);
    ASSERT_NE(out, nullptr);
    std::string s(out);
    EXPECT_NE(s.find("Minimal"), std::string::npos);

    pb_free_string(out);
    pb_plan_free(plan);
}
