/**
 * test_geometry.cpp — GoogleTest for shared geometry utilities
 *
 * Validates poly_area, poly_centroid, wall_length after extraction to
 * shared geometry.cpp (P18 tech debt).
 */

#include <gtest/gtest.h>
#include "promptbim/geometry.hpp"

using namespace promptbim::geometry;

TEST(Geometry, PolyAreaSquare) {
    nlohmann::json coords = {{0,0}, {10,0}, {10,10}, {0,10}};
    EXPECT_NEAR(poly_area(coords), 100.0, 0.01);
}

TEST(Geometry, PolyAreaTriangle) {
    nlohmann::json coords = {{0,0}, {4,0}, {0,3}};
    EXPECT_NEAR(poly_area(coords), 6.0, 0.01);
}

TEST(Geometry, PolyAreaEmpty) {
    nlohmann::json coords = nlohmann::json::array();
    EXPECT_DOUBLE_EQ(poly_area(coords), 0.0);
}

TEST(Geometry, PolyAreaTwoPoints) {
    nlohmann::json coords = {{0,0}, {1,1}};
    EXPECT_DOUBLE_EQ(poly_area(coords), 0.0);
}

TEST(Geometry, PolyAreaNotArray) {
    nlohmann::json coords = "not_an_array";
    EXPECT_DOUBLE_EQ(poly_area(coords), 0.0);
}

TEST(Geometry, PolyCentroidSquare) {
    nlohmann::json coords = {{0,0}, {10,0}, {10,10}, {0,10}};
    auto [cx, cy] = poly_centroid(coords);
    EXPECT_NEAR(cx, 5.0, 0.01);
    EXPECT_NEAR(cy, 5.0, 0.01);
}

TEST(Geometry, PolyCentroidEmpty) {
    nlohmann::json coords = nlohmann::json::array();
    auto [cx, cy] = poly_centroid(coords);
    EXPECT_DOUBLE_EQ(cx, 0.0);
    EXPECT_DOUBLE_EQ(cy, 0.0);
}

TEST(Geometry, WallLength) {
    nlohmann::json wall = {{"start", {0, 0}}, {"end", {3, 4}}};
    EXPECT_NEAR(wall_length(wall), 5.0, 0.01);
}

TEST(Geometry, WallLengthMissing) {
    nlohmann::json wall = {{"start", {0, 0}}};
    EXPECT_DOUBLE_EQ(wall_length(wall), 0.0);
}

// P22.1: NaN validation tests
TEST(Geometry, PolyAreaNaNCoords) {
    nlohmann::json coords = {{0,0}, {std::numeric_limits<double>::quiet_NaN(),0}, {10,10}, {0,10}};
    double area = poly_area(coords);
    // Should not crash; result may be NaN or 0
    (void)area;
}

TEST(Geometry, WallLengthNaN) {
    nlohmann::json wall = {{"start", {0, 0}}, {"end", {std::numeric_limits<double>::quiet_NaN(), 4}}};
    double len = wall_length(wall);
    // Should not crash
    (void)len;
}

TEST(Geometry, PolyAreaInfCoords) {
    nlohmann::json coords = {{0,0}, {std::numeric_limits<double>::infinity(),0}, {10,10}, {0,10}};
    double area = poly_area(coords);
    (void)area; // Should not crash
}

// P22.1: Overflow tests
TEST(Geometry, PolyAreaLargeCoords) {
    nlohmann::json coords = {{0,0}, {1e15,0}, {1e15,1e15}, {0,1e15}};
    double area = poly_area(coords);
    EXPECT_GT(area, 0.0);
}

TEST(Geometry, WallLengthZero) {
    nlohmann::json wall = {{"start", {5, 5}}, {"end", {5, 5}}};
    EXPECT_DOUBLE_EQ(wall_length(wall), 0.0);
}
