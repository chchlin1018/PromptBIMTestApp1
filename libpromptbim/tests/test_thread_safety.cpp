/**
 * test_thread_safety.cpp — GoogleTest for concurrent C++ engine usage
 *
 * P22: Validates thread safety of IFC generation and GIS parsing
 * under concurrent access from multiple threads.
 */

#include <gtest/gtest.h>
#include "promptbim/ifc_generator.hpp"
#include "promptbim/gis_engine.hpp"
#include "promptbim/promptbim.h"

#include <atomic>
#include <thread>
#include <vector>

using namespace promptbim;

static const char* THREAD_PLAN = R"({
    "name": "Thread Test Building",
    "stories": [{
        "name": "1F",
        "elevation_m": 0.0,
        "height_m": 3.0,
        "walls": [
            {"start": [0,0], "end": [10,0], "thickness_m": 0.2, "wall_type": "exterior"},
            {"start": [10,0], "end": [10,8], "thickness_m": 0.2, "wall_type": "exterior"},
            {"start": [10,8], "end": [0,8], "thickness_m": 0.2, "wall_type": "exterior"},
            {"start": [0,8], "end": [0,0], "thickness_m": 0.2, "wall_type": "exterior"}
        ]
    }]
})";

static const char* THREAD_GEOJSON = R"({
    "type": "Feature",
    "properties": {"name": "ThreadTest"},
    "geometry": {
        "type": "Polygon",
        "coordinates": [[[0,0],[10,0],[10,10],[0,10],[0,0]]]
    }
})";

TEST(ThreadSafety, ConcurrentIFCGeneration) {
    // P22: Multiple threads generating IFC simultaneously
    constexpr int NUM_THREADS = 4;
    std::atomic<int> success_count{0};
    std::vector<std::thread> threads;

    for (int i = 0; i < NUM_THREADS; ++i) {
        threads.emplace_back([&]() {
            IFCGenerator gen;
            std::string ifc = gen.generate_string(THREAD_PLAN);
            if (!ifc.empty() &&
                ifc.find("ISO-10303-21;") != std::string::npos &&
                ifc.find("IFCWALL") != std::string::npos) {
                success_count++;
            }
        });
    }

    for (auto& t : threads) t.join();
    EXPECT_EQ(success_count.load(), NUM_THREADS);
}

TEST(ThreadSafety, ConcurrentGISParsing) {
    // P22: Multiple threads parsing GeoJSON simultaneously
    constexpr int NUM_THREADS = 4;
    std::atomic<int> success_count{0};
    std::vector<std::thread> threads;

    for (int i = 0; i < NUM_THREADS; ++i) {
        threads.emplace_back([&]() {
            GISEngine engine;
            try {
                auto lp = engine.parse_geojson(THREAD_GEOJSON);
                if (lp.boundary.size() == 4 && lp.name == "ThreadTest") {
                    success_count++;
                }
            } catch (...) {
                // Should not throw
            }
        });
    }

    for (auto& t : threads) t.join();
    EXPECT_EQ(success_count.load(), NUM_THREADS);
}

// P22.1: IFC thread safety stress test — high contention
TEST(ThreadSafety, IFCStressHighContention) {
    constexpr int NUM_THREADS = 8;
    std::atomic<int> success_count{0};
    std::vector<std::thread> threads;

    for (int i = 0; i < NUM_THREADS; ++i) {
        threads.emplace_back([&]() {
            IFCGenerator gen;
            std::string ifc = gen.generate_string(THREAD_PLAN);
            if (!ifc.empty() && ifc.find("IFCWALL") != std::string::npos) {
                success_count++;
            }
        });
    }

    for (auto& t : threads) t.join();
    EXPECT_EQ(success_count.load(), NUM_THREADS);
}

// P22.1: Mixed read/write thread safety
TEST(ThreadSafety, ConcurrentIFCAndGIS) {
    constexpr int NUM_THREADS = 4;
    std::atomic<int> ifc_success{0};
    std::atomic<int> gis_success{0};
    std::vector<std::thread> threads;

    for (int i = 0; i < NUM_THREADS; ++i) {
        // Even threads do IFC, odd threads do GIS
        if (i % 2 == 0) {
            threads.emplace_back([&]() {
                IFCGenerator gen;
                std::string ifc = gen.generate_string(THREAD_PLAN);
                if (!ifc.empty()) ifc_success++;
            });
        } else {
            threads.emplace_back([&]() {
                GISEngine engine;
                auto lp = engine.parse_geojson(THREAD_GEOJSON);
                if (lp.boundary.size() == 4) gis_success++;
            });
        }
    }

    for (auto& t : threads) t.join();
    EXPECT_EQ(ifc_success.load(), NUM_THREADS / 2);
    EXPECT_EQ(gis_success.load(), NUM_THREADS / 2);
}

// P22.1: Thread safety with CABI functions
TEST(ThreadSafety, CABIConcurrentPlanParse) {
    constexpr int NUM_THREADS = 4;
    std::atomic<int> success_count{0};
    std::vector<std::thread> threads;

    for (int i = 0; i < NUM_THREADS; ++i) {
        threads.emplace_back([&]() {
            PBPlan* plan = pb_plan_from_json(THREAD_PLAN);
            if (plan != nullptr) {
                char* json = pb_plan_to_json(plan);
                if (json != nullptr) {
                    success_count++;
                    pb_free_string(json);
                }
                pb_plan_free(plan);
            }
        });
    }

    for (auto& t : threads) t.join();
    EXPECT_EQ(success_count.load(), NUM_THREADS);
}
