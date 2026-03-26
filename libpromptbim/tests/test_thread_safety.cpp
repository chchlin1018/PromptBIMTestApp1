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
