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
