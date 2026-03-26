/**
 * gis_engine.hpp — GIS Engine for land parcel parsing, geometry ops, coord projection
 *
 * Replaces Python geopandas/shapely/pyproj with pure C++ implementation.
 * Supports: GeoJSON, Shapefile (DBF+SHP), DXF parsing
 *           Setback/buffer geometry, WGS84 → TWD97 projection
 *
 * No external GIS library dependencies — uses nlohmann/json + custom parsers.
 */

#pragma once

#include <string>
#include <vector>
#include <nlohmann/json.hpp>

namespace promptbim {

// ---------------------------------------------------------------------------
// Point2D / Polygon
// ---------------------------------------------------------------------------

struct Point2D {
    double x = 0.0;
    double y = 0.0;
};

// ---------------------------------------------------------------------------
// LandParcel — parsed land data
// ---------------------------------------------------------------------------

struct LandParcel {
    std::string name;
    std::vector<Point2D> boundary;       // outer ring (metres, local coords)
    double area_sqm = 0.0;
    std::string crs;                     // e.g. "EPSG:4326" or "EPSG:3826"
    nlohmann::json properties;           // arbitrary attributes

    nlohmann::json to_json() const;
    static LandParcel from_json(const nlohmann::json& j);
};

// ---------------------------------------------------------------------------
// GISEngine
// ---------------------------------------------------------------------------

class GISEngine {
public:
    // --- Parsing -----------------------------------------------------------

    /** Parse GeoJSON file/string to LandParcel. */
    LandParcel parse_geojson(const std::string& geojson_str) const;
    LandParcel parse_geojson_file(const std::string& path) const;

    /** Parse Shapefile (.shp) to LandParcel.
     *  Reads the binary SHP main file (simplified: first polygon only). */
    LandParcel parse_shapefile(const std::string& shp_path) const;

    /** Parse DXF file to LandParcel (LWPOLYLINE entities). */
    LandParcel parse_dxf(const std::string& dxf_path) const;

    // --- Geometry operations -----------------------------------------------

    /** Compute area of polygon using Shoelace formula (sq metres). */
    static double compute_area(const std::vector<Point2D>& poly);

    /** Compute centroid of polygon. */
    static Point2D compute_centroid(const std::vector<Point2D>& poly);

    /** Compute perimeter length of polygon. */
    static double compute_perimeter(const std::vector<Point2D>& poly);

    /** Apply setback (inward offset) to polygon.
     *  Uses simplified straight-skeleton approach for convex/near-convex parcels. */
    static std::vector<Point2D> apply_setback(
        const std::vector<Point2D>& boundary,
        double setback_m);

    /** Apply buffer (outward offset) to polygon. */
    static std::vector<Point2D> apply_buffer(
        const std::vector<Point2D>& boundary,
        double buffer_m);

    // --- Coordinate projection ---------------------------------------------

    /** Convert WGS84 (lon, lat) to TWD97 TM2 (EPSG:3826).
     *  Uses Transverse Mercator projection with Taiwan parameters. */
    static Point2D wgs84_to_twd97(double longitude, double latitude);

    /** Convert TWD97 TM2 (E, N) back to WGS84 (lon, lat). */
    static Point2D twd97_to_wgs84(double easting, double northing);

    /** Project all points in a boundary from WGS84 to TWD97. */
    static std::vector<Point2D> project_boundary_to_twd97(
        const std::vector<Point2D>& wgs84_pts);

private:
    // --- Internal helpers --------------------------------------------------
    static std::vector<Point2D> extract_polygon_coords(const nlohmann::json& geometry);
    static std::vector<Point2D> parse_shp_polygon(const std::string& path);
};

} // namespace promptbim
