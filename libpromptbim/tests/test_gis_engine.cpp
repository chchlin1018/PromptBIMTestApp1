/**
 * test_gis_engine.cpp — GoogleTest for GIS Engine
 *
 * Covers: GeoJSON parsing, Shapefile parsing, DXF parsing,
 *         setback/buffer geometry, coordinate projection (WGS84 ↔ TWD97),
 *         C ABI functions.
 */

#include <gtest/gtest.h>
#include "promptbim/gis_engine.hpp"
#include "promptbim/promptbim.h"

#include <cmath>
#include <fstream>
#include <nlohmann/json.hpp>

using namespace promptbim;

// =========================================================================
// Helper: write temp file
// =========================================================================

static std::string write_temp_file(const std::string& content,
                                    const std::string& suffix) {
    std::string path = "/tmp/test_gis_" + suffix;
    std::ofstream ofs(path);
    ofs << content;
    ofs.close();
    return path;
}

// =========================================================================
// GeoJSON Parsing
// =========================================================================

static const char* SAMPLE_GEOJSON = R"({
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {"name": "TestParcel", "LAND_ID": "A-001"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]]
        }
    }]
})";

TEST(GISEngine, ParseGeoJSONString) {
    GISEngine engine;
    auto lp = engine.parse_geojson(SAMPLE_GEOJSON);

    EXPECT_EQ(lp.name, "TestParcel");
    EXPECT_EQ(lp.crs, "EPSG:4326");
    EXPECT_EQ(lp.boundary.size(), 4u);
    EXPECT_NEAR(lp.area_sqm, 100.0, 0.01);
}

TEST(GISEngine, ParseGeoJSONFile) {
    auto path = write_temp_file(SAMPLE_GEOJSON, "sample.geojson");
    GISEngine engine;
    auto lp = engine.parse_geojson_file(path);

    EXPECT_EQ(lp.name, "TestParcel");
    EXPECT_EQ(lp.boundary.size(), 4u);
    EXPECT_NEAR(lp.area_sqm, 100.0, 0.01);
}

TEST(GISEngine, ParseGeoJSONFeature) {
    const char* feature_json = R"({
        "type": "Feature",
        "properties": {"name": "Single"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[0,0],[20,0],[20,5],[0,5],[0,0]]]
        }
    })";
    GISEngine engine;
    auto lp = engine.parse_geojson(feature_json);
    EXPECT_EQ(lp.name, "Single");
    EXPECT_NEAR(lp.area_sqm, 100.0, 0.01);
}

TEST(GISEngine, ParseGeoJSONBarePolygon) {
    const char* poly_json = R"({
        "type": "Polygon",
        "coordinates": [[[0,0],[5,0],[5,5],[0,5],[0,0]]]
    })";
    GISEngine engine;
    auto lp = engine.parse_geojson(poly_json);
    EXPECT_EQ(lp.boundary.size(), 4u);
    EXPECT_NEAR(lp.area_sqm, 25.0, 0.01);
}

TEST(GISEngine, ParseGeoJSONMultiPolygon) {
    const char* multi_json = R"({
        "type": "MultiPolygon",
        "coordinates": [[[[0,0],[10,0],[10,10],[0,10],[0,0]]]]
    })";
    GISEngine engine;
    auto lp = engine.parse_geojson(multi_json);
    EXPECT_EQ(lp.boundary.size(), 4u);
    EXPECT_NEAR(lp.area_sqm, 100.0, 0.01);
}

TEST(GISEngine, ParseGeoJSONInvalidFile) {
    GISEngine engine;
    EXPECT_THROW(engine.parse_geojson_file("/nonexistent/file.geojson"),
                 std::runtime_error);
}

// =========================================================================
// DXF Parsing
// =========================================================================

static const char* SAMPLE_DXF = R"(0
SECTION
2
ENTITIES
0
LWPOLYLINE
10
0.0
20
0.0
10
10.0
20
0.0
10
10.0
20
10.0
10
0.0
20
10.0
0
ENDSEC
0
EOF
)";

TEST(GISEngine, ParseDXF) {
    auto path = write_temp_file(SAMPLE_DXF, "sample.dxf");
    GISEngine engine;
    auto lp = engine.parse_dxf(path);

    EXPECT_EQ(lp.boundary.size(), 4u);
    EXPECT_NEAR(lp.area_sqm, 100.0, 0.01);
}

TEST(GISEngine, ParseDXFInvalidFile) {
    GISEngine engine;
    EXPECT_THROW(engine.parse_dxf("/nonexistent/file.dxf"),
                 std::runtime_error);
}

// =========================================================================
// Geometry Operations
// =========================================================================

TEST(GISGeometry, ComputeArea) {
    // 10x10 square
    std::vector<Point2D> square = {{0,0},{10,0},{10,10},{0,10}};
    EXPECT_NEAR(GISEngine::compute_area(square), 100.0, 0.001);
}

TEST(GISGeometry, ComputeAreaTriangle) {
    std::vector<Point2D> tri = {{0,0},{10,0},{5,10}};
    EXPECT_NEAR(GISEngine::compute_area(tri), 50.0, 0.001);
}

TEST(GISGeometry, ComputeAreaEmpty) {
    std::vector<Point2D> empty;
    EXPECT_NEAR(GISEngine::compute_area(empty), 0.0, 0.001);
}

TEST(GISGeometry, ComputeCentroid) {
    std::vector<Point2D> square = {{0,0},{10,0},{10,10},{0,10}};
    auto c = GISEngine::compute_centroid(square);
    EXPECT_NEAR(c.x, 5.0, 0.001);
    EXPECT_NEAR(c.y, 5.0, 0.001);
}

TEST(GISGeometry, ComputePerimeter) {
    std::vector<Point2D> square = {{0,0},{10,0},{10,10},{0,10}};
    EXPECT_NEAR(GISEngine::compute_perimeter(square), 40.0, 0.001);
}

TEST(GISGeometry, SetbackReducesArea) {
    std::vector<Point2D> square = {{0,0},{100,0},{100,100},{0,100}};
    auto setback = GISEngine::apply_setback(square, 10.0);
    double original_area = GISEngine::compute_area(square);
    double setback_area = GISEngine::compute_area(setback);
    EXPECT_LT(setback_area, original_area);
    EXPECT_GT(setback_area, 0.0);
}

TEST(GISGeometry, SetbackZeroReturnsOriginal) {
    std::vector<Point2D> square = {{0,0},{10,0},{10,10},{0,10}};
    auto result = GISEngine::apply_setback(square, 0.0);
    EXPECT_EQ(result.size(), square.size());
    EXPECT_NEAR(result[0].x, square[0].x, 0.001);
}

TEST(GISGeometry, BufferIncreasesArea) {
    std::vector<Point2D> square = {{0,0},{100,0},{100,100},{0,100}};
    auto buffered = GISEngine::apply_buffer(square, 10.0);
    double original_area = GISEngine::compute_area(square);
    double buffer_area = GISEngine::compute_area(buffered);
    EXPECT_GT(buffer_area, original_area);
}

// =========================================================================
// Coordinate Projection: WGS84 ↔ TWD97
// =========================================================================

TEST(GISProjection, WGS84ToTWD97TaipeiStation) {
    // Taipei Main Station: ~121.5170°E, 25.0478°N
    // TWD97 TM2: easting near 300000 range, northing near 2770000 range
    auto twd = GISEngine::wgs84_to_twd97(121.5170, 25.0478);
    // Easting should be > false easting (250000) for lon > 121°
    EXPECT_GT(twd.x, 250000.0);
    EXPECT_LT(twd.x, 350000.0);
    // Northing should be in Taiwan range (~2500000-2800000)
    EXPECT_GT(twd.y, 2700000.0);
    EXPECT_LT(twd.y, 2800000.0);
}

TEST(GISProjection, TWD97ToWGS84RoundTrip) {
    // Round-trip: WGS84 → TWD97 → WGS84 should be identity
    double lon_in = 121.0;
    double lat_in = 24.5;
    auto twd = GISEngine::wgs84_to_twd97(lon_in, lat_in);
    auto wgs = GISEngine::twd97_to_wgs84(twd.x, twd.y);
    EXPECT_NEAR(wgs.x, lon_in, 1e-5);  // ~1m precision
    EXPECT_NEAR(wgs.y, lat_in, 1e-5);
}

TEST(GISProjection, TWD97ToWGS84RoundTrip2) {
    double lon_in = 120.5;
    double lat_in = 23.0;
    auto twd = GISEngine::wgs84_to_twd97(lon_in, lat_in);
    auto wgs = GISEngine::twd97_to_wgs84(twd.x, twd.y);
    EXPECT_NEAR(wgs.x, lon_in, 1e-5);
    EXPECT_NEAR(wgs.y, lat_in, 1e-5);
}

TEST(GISProjection, ProjectBoundary) {
    // Project a small boundary near Taiwan
    std::vector<Point2D> wgs = {
        {121.0, 25.0}, {121.01, 25.0}, {121.01, 25.01}, {121.0, 25.01}
    };
    auto twd = GISEngine::project_boundary_to_twd97(wgs);
    EXPECT_EQ(twd.size(), 4u);
    // All TWD97 eastings should be near 250000 (central meridian)
    for (const auto& pt : twd) {
        EXPECT_GT(pt.x, 200000.0);
        EXPECT_LT(pt.x, 400000.0);
        EXPECT_GT(pt.y, 2700000.0);
    }
}

// =========================================================================
// LandParcel JSON serialization
// =========================================================================

TEST(GISLandParcel, ToFromJSON) {
    LandParcel lp;
    lp.name = "test-lot";
    lp.boundary = {{0,0},{10,0},{10,10},{0,10}};
    lp.area_sqm = 100.0;
    lp.crs = "EPSG:3826";

    auto j = lp.to_json();
    auto lp2 = LandParcel::from_json(j);
    EXPECT_EQ(lp2.name, "test-lot");
    EXPECT_EQ(lp2.boundary.size(), 4u);
    EXPECT_NEAR(lp2.area_sqm, 100.0, 0.01);
    EXPECT_EQ(lp2.crs, "EPSG:3826");
}

// =========================================================================
// C ABI Tests
// =========================================================================

TEST(GISCABI, LandFromGeoJSONFile) {
    auto path = write_temp_file(SAMPLE_GEOJSON, "cabi_test.geojson");
    PBLandParcel* lp = pb_land_from_geojson(path.c_str());
    ASSERT_NE(lp, nullptr);

    char* json = pb_land_to_json(lp);
    ASSERT_NE(json, nullptr);

    auto j = nlohmann::json::parse(json);
    EXPECT_EQ(j["name"].get<std::string>(), "TestParcel");
    EXPECT_NEAR(j["area_sqm"].get<double>(), 100.0, 0.01);

    pb_free_string(json);
    pb_land_free(lp);
}

TEST(GISCABI, LandFromGeoJSONString) {
    PBLandParcel* lp = pb_land_from_geojson_string(SAMPLE_GEOJSON);
    ASSERT_NE(lp, nullptr);

    char* json = pb_land_to_json(lp);
    ASSERT_NE(json, nullptr);

    auto j = nlohmann::json::parse(json);
    EXPECT_EQ(j["name"].get<std::string>(), "TestParcel");

    pb_free_string(json);
    pb_land_free(lp);
}

TEST(GISCABI, LandFromInvalidPath) {
    PBLandParcel* lp = pb_land_from_geojson("/nonexistent.geojson");
    EXPECT_EQ(lp, nullptr);
}

TEST(GISCABI, LandFromDXF) {
    auto path = write_temp_file(SAMPLE_DXF, "cabi_test.dxf");
    PBLandParcel* lp = pb_land_from_dxf(path.c_str());
    ASSERT_NE(lp, nullptr);

    char* json = pb_land_to_json(lp);
    ASSERT_NE(json, nullptr);

    auto j = nlohmann::json::parse(json);
    EXPECT_NEAR(j["area_sqm"].get<double>(), 100.0, 0.01);

    pb_free_string(json);
    pb_land_free(lp);
}

TEST(GISCABI, LandFreeNull) {
    pb_land_free(nullptr); // should not crash
}

TEST(GISCABI, LandToJsonNull) {
    char* json = pb_land_to_json(nullptr);
    EXPECT_EQ(json, nullptr);
}

// P22.1: GIS non-convex setback edge cases
TEST(GISGeometry, NonConvexLShapeSetback) {
    // L-shaped parcel
    std::vector<Point2D> l_shape = {
        {0,0}, {20,0}, {20,10}, {10,10}, {10,20}, {0,20}
    };
    auto result = GISEngine::apply_setback(l_shape, 2.0);
    // Should not crash on non-convex polygon
    EXPECT_GT(result.size(), 0u);
    double original_area = GISEngine::compute_area(l_shape);
    double setback_area = GISEngine::compute_area(result);
    EXPECT_LT(setback_area, original_area);
}

TEST(GISGeometry, NonConvexTShapeSetback) {
    // T-shaped parcel
    std::vector<Point2D> t_shape = {
        {0,0}, {30,0}, {30,10}, {20,10}, {20,20}, {10,20}, {10,10}, {0,10}
    };
    auto result = GISEngine::apply_setback(t_shape, 1.5);
    EXPECT_GT(result.size(), 0u);
}

TEST(GISGeometry, TrapezoidSetback) {
    // Trapezoid (non-rectangular, still convex)
    std::vector<Point2D> trapezoid = {
        {5,0}, {25,0}, {20,15}, {10,15}
    };
    auto result = GISEngine::apply_setback(trapezoid, 2.0);
    EXPECT_GT(result.size(), 0u);
    double original_area = GISEngine::compute_area(trapezoid);
    double setback_area = GISEngine::compute_area(result);
    EXPECT_LT(setback_area, original_area);
}

// P22.1: Sanitizer-friendly tests
TEST(GISGeometry, EmptyPolygonSetback) {
    std::vector<Point2D> empty;
    auto result = GISEngine::apply_setback(empty, 2.0);
    EXPECT_EQ(result.size(), 0u);
}

TEST(GISGeometry, SinglePointSetback) {
    std::vector<Point2D> point = {{5,5}};
    auto result = GISEngine::apply_setback(point, 2.0);
    // Should handle gracefully
    (void)result;
}
