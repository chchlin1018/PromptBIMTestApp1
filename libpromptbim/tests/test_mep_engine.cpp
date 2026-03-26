/**
 * test_mep_engine.cpp — GoogleTest for MEP A* Pathfinding Engine
 *
 * Covers: basic path, obstacle avoidance, no path, performance, grid conversion,
 *         path simplification, wall obstacles, bbox obstacles.
 */

#include <gtest/gtest.h>
#include "promptbim/mep_engine.hpp"

using namespace promptbim;

// -----------------------------------------------------------------------
// Basic pathfinding
// -----------------------------------------------------------------------

TEST(MEPEngine, StraightPath) {
    MEPEngine engine(0.3);
    auto path = engine.find_path({0, 0, 0}, {2.1, 0, 0});
    EXPECT_FALSE(path.waypoints.empty());
    EXPECT_GT(path.total_length_m, 1.9);
    EXPECT_LT(path.total_length_m, 2.5);
}

TEST(MEPEngine, SameStartEnd) {
    MEPEngine engine(0.3);
    auto path = engine.find_path({1.0, 2.0, 3.0}, {1.0, 2.0, 3.0});
    EXPECT_EQ(path.waypoints.size(), 1u);
    EXPECT_DOUBLE_EQ(path.total_length_m, 0.0);
}

TEST(MEPEngine, VerticalPath) {
    MEPEngine engine(0.3);
    auto path = engine.find_path({0, 0, 0}, {0, 0, 3.0});
    EXPECT_FALSE(path.waypoints.empty());
    EXPECT_GT(path.total_length_m, 2.5);
    EXPECT_LT(path.total_length_m, 3.5);
}

// -----------------------------------------------------------------------
// Obstacle avoidance
// -----------------------------------------------------------------------

TEST(MEPEngine, PathAroundObstacle) {
    MEPEngine engine(0.3);
    // Place obstacle at midpoint
    auto mid = engine.to_grid({1.0, 0, 0});
    engine.add_obstacle(mid.gx, mid.gy, mid.gz);

    auto path = engine.find_path({0, 0, 0}, {2.1, 0, 0});
    EXPECT_FALSE(path.waypoints.empty());
    // Path should be longer than straight line due to detour
    EXPECT_GT(path.total_length_m, 2.1);
}

TEST(MEPEngine, NoPathBlocked) {
    MEPEngine engine(0.3);
    // Surround the goal with obstacles
    auto goal = engine.to_grid({1.5, 0, 0});
    engine.add_obstacle(goal.gx, goal.gy, goal.gz);

    auto path = engine.find_path({0, 0, 0}, {1.5, 0, 0});
    EXPECT_TRUE(path.waypoints.empty());
    EXPECT_DOUBLE_EQ(path.total_length_m, 0.0);
}

// -----------------------------------------------------------------------
// Obstacle from bbox
// -----------------------------------------------------------------------

TEST(MEPEngine, ObstaclesFromBBox) {
    MEPEngine engine(0.3);
    engine.add_obstacles_from_bbox({0.5, -0.5, -0.5}, {1.5, 0.5, 0.5});
    EXPECT_GT(engine.obstacle_count(), 0u);

    // Path should go around the bbox
    auto path = engine.find_path({0, 0, 0}, {3.0, 0, 0});
    EXPECT_FALSE(path.waypoints.empty());
    EXPECT_GT(path.total_length_m, 3.0); // must detour
}

// -----------------------------------------------------------------------
// Obstacle from walls
// -----------------------------------------------------------------------

TEST(MEPEngine, ObstaclesFromWalls) {
    MEPEngine engine(0.3);
    nlohmann::json walls = nlohmann::json::array({
        {{"start", {1.0, -2.0}}, {"end", {1.0, 2.0}}, {"thickness_m", 0.2}}
    });
    engine.add_obstacles_from_walls(walls, 0.0, 3.0);
    EXPECT_GT(engine.obstacle_count(), 0u);

    // Path must go around the wall
    auto path = engine.find_path({0, 0, 1.0}, {3.0, 0, 1.0});
    EXPECT_FALSE(path.waypoints.empty());
}

// -----------------------------------------------------------------------
// Grid conversion
// -----------------------------------------------------------------------

TEST(MEPEngine, GridConversion) {
    MEPEngine engine(0.3);
    Point3D p = {1.5, 2.4, 0.9};
    auto g = engine.to_grid(p);
    EXPECT_EQ(g.gx, 5);
    EXPECT_EQ(g.gy, 8);
    EXPECT_EQ(g.gz, 3);

    auto w = engine.to_world(g);
    EXPECT_NEAR(w.x, 1.5, 0.01);
    EXPECT_NEAR(w.y, 2.4, 0.01);
    EXPECT_NEAR(w.z, 0.9, 0.01);
}

// -----------------------------------------------------------------------
// Path simplification
// -----------------------------------------------------------------------

TEST(MEPEngine, PathSimplification) {
    MEPEngine engine(0.3);
    // Long straight path should be simplified to 2 waypoints
    auto path = engine.find_path({0, 0, 0}, {6.0, 0, 0});
    EXPECT_FALSE(path.waypoints.empty());
    // Simplified path: start and end only (all collinear)
    EXPECT_EQ(path.waypoints.size(), 2u);
    EXPECT_EQ(path.segments.size(), 1u);
}

// -----------------------------------------------------------------------
// Performance benchmark
// -----------------------------------------------------------------------

TEST(MEPEngine, PerformanceBenchmark) {
    MEPEngine engine(0.3);
    // Add some obstacles to make it non-trivial
    for (int x = 3; x <= 7; ++x)
        for (int y = -2; y <= 2; ++y)
            engine.add_obstacle(x, y, 0);

    auto start = std::chrono::high_resolution_clock::now();
    auto path = engine.find_path({0, 0, 0}, {6.0, 0, 0});
    auto end = std::chrono::high_resolution_clock::now();

    double ms = std::chrono::duration<double, std::milli>(end - start).count();
    EXPECT_FALSE(path.waypoints.empty());
    // A* should complete well under 100ms for this grid
    EXPECT_LT(ms, 100.0);
}

// -----------------------------------------------------------------------
// JSON interface: plan_mep
// -----------------------------------------------------------------------

TEST(MEPEngine, PlanMepJSON) {
    MEPEngine engine(0.3);
    nlohmann::json plan = {
        {"building_footprint", {{0,0}, {10,0}, {10,8}, {0,8}}},
        {"stories", {{
            {"name", "1F"},
            {"elevation_m", 0.0},
            {"height_m", 3.0},
            {"spaces", {{
                {"name", "Office"},
                {"boundary", {{2,2}, {8,2}, {8,6}, {2,6}}},
            }}},
        }}},
    };
    std::string result = engine.plan_mep(plan.dump(), "{}");
    auto j = nlohmann::json::parse(result);
    EXPECT_TRUE(j.contains("routes"));
    EXPECT_TRUE(j.contains("equipment"));
}

TEST(MEPEngine, PlanMepInvalidJSON) {
    MEPEngine engine;
    std::string result = engine.plan_mep("not-json", "");
    auto j = nlohmann::json::parse(result);
    EXPECT_TRUE(j.contains("error"));
}

// -----------------------------------------------------------------------
// Clear obstacles
// -----------------------------------------------------------------------

TEST(MEPEngine, ClearObstacles) {
    MEPEngine engine(0.3);
    engine.add_obstacle(1, 1, 1);
    EXPECT_EQ(engine.obstacle_count(), 1u);
    engine.clear_obstacles();
    EXPECT_EQ(engine.obstacle_count(), 0u);
}
