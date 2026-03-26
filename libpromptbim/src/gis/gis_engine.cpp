/**
 * gis_engine.cpp — GIS Engine implementation
 *
 * Pure C++ implementation of land parcel parsing, geometry operations,
 * and WGS84 ↔ TWD97 coordinate projection.
 *
 * No external GIS library dependencies.
 */

#include "promptbim/gis_engine.hpp"
#include "promptbim/promptbim.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <sstream>
#include <stdexcept>

namespace promptbim {

// =========================================================================
// Constants for TWD97 Transverse Mercator projection
// =========================================================================
namespace {

constexpr double PI = 3.14159265358979323846;
constexpr double DEG2RAD = PI / 180.0;
constexpr double RAD2DEG = 180.0 / PI;

// GRS80 ellipsoid (used by TWD97)
constexpr double GRS80_A = 6378137.0;           // semi-major axis (m)
constexpr double GRS80_F = 1.0 / 298.257222101; // flattening
constexpr double GRS80_B = GRS80_A * (1.0 - GRS80_F); // semi-minor axis
constexpr double GRS80_E2 = 2.0 * GRS80_F - GRS80_F * GRS80_F; // eccentricity^2
constexpr double GRS80_EP2 = GRS80_E2 / (1.0 - GRS80_E2);      // second eccentricity^2

// TWD97 TM2 zone parameters (121°E central meridian)
constexpr double TM2_K0 = 0.9999;         // scale factor
constexpr double TM2_LON0 = 121.0;        // central meridian (degrees)
constexpr double TM2_FE = 250000.0;       // false easting (m)
constexpr double TM2_FN = 0.0;            // false northing (m)

// Helper: read little-endian int32 from bytes
inline int32_t read_le_int32(const uint8_t* p) {
    return static_cast<int32_t>(
        p[0] | (p[1] << 8) | (p[2] << 16) | (p[3] << 24));
}

// Helper: read little-endian double from bytes
inline double read_le_double(const uint8_t* p) {
    double val;
    std::memcpy(&val, p, 8);
    return val;
}

// Helper: read big-endian int32 from bytes
inline int32_t read_be_int32(const uint8_t* p) {
    return static_cast<int32_t>(
        (p[0] << 24) | (p[1] << 16) | (p[2] << 8) | p[3]);
}

} // anonymous namespace

// =========================================================================
// LandParcel JSON serialization
// =========================================================================

nlohmann::json LandParcel::to_json() const {
    nlohmann::json coords = nlohmann::json::array();
    for (const auto& pt : boundary) {
        coords.push_back({pt.x, pt.y});
    }
    return {
        {"name",       name},
        {"boundary",   coords},
        {"area_sqm",   area_sqm},
        {"crs",        crs},
        {"properties", properties},
    };
}

LandParcel LandParcel::from_json(const nlohmann::json& j) {
    LandParcel lp;
    if (j.contains("name")) lp.name = j["name"].get<std::string>();
    if (j.contains("crs"))  lp.crs  = j["crs"].get<std::string>();
    if (j.contains("area_sqm")) lp.area_sqm = j["area_sqm"].get<double>();
    if (j.contains("properties")) lp.properties = j["properties"];

    if (j.contains("boundary") && j["boundary"].is_array()) {
        for (const auto& pt : j["boundary"]) {
            if (pt.is_array() && pt.size() >= 2) {
                lp.boundary.push_back({pt[0].get<double>(), pt[1].get<double>()});
            }
        }
    }
    return lp;
}

// =========================================================================
// GeoJSON Parsing
// =========================================================================

std::vector<Point2D> GISEngine::extract_polygon_coords(const nlohmann::json& geometry) {
    std::vector<Point2D> pts;
    if (!geometry.contains("type") || !geometry.contains("coordinates"))
        return pts;

    const auto& type = geometry["type"].get<std::string>();
    if (type == "Polygon") {
        // First ring = outer boundary
        const auto& ring = geometry["coordinates"][0];
        for (const auto& coord : ring) {
            if (coord.is_array() && coord.size() >= 2) {
                pts.push_back({coord[0].get<double>(), coord[1].get<double>()});
            }
        }
        // Remove closing point if same as first
        if (pts.size() > 1) {
            const auto& f = pts.front();
            const auto& l = pts.back();
            if (std::abs(f.x - l.x) < 1e-12 && std::abs(f.y - l.y) < 1e-12) {
                pts.pop_back();
            }
        }
    } else if (type == "MultiPolygon") {
        // Take the first polygon
        if (!geometry["coordinates"].empty()) {
            const auto& ring = geometry["coordinates"][0][0];
            for (const auto& coord : ring) {
                if (coord.is_array() && coord.size() >= 2) {
                    pts.push_back({coord[0].get<double>(), coord[1].get<double>()});
                }
            }
            if (pts.size() > 1) {
                const auto& f = pts.front();
                const auto& l = pts.back();
                if (std::abs(f.x - l.x) < 1e-12 && std::abs(f.y - l.y) < 1e-12) {
                    pts.pop_back();
                }
            }
        }
    }
    return pts;
}

LandParcel GISEngine::parse_geojson(const std::string& geojson_str) const {
    auto j = nlohmann::json::parse(geojson_str);
    LandParcel lp;
    lp.crs = "EPSG:4326"; // default for GeoJSON

    nlohmann::json geom;
    nlohmann::json props;

    if (j.contains("type")) {
        const auto& type = j["type"].get<std::string>();
        if (type == "FeatureCollection") {
            if (j.contains("features") && !j["features"].empty()) {
                const auto& feat = j["features"][0];
                geom = feat.value("geometry", nlohmann::json{});
                props = feat.value("properties", nlohmann::json{});
            }
        } else if (type == "Feature") {
            geom = j.value("geometry", nlohmann::json{});
            props = j.value("properties", nlohmann::json{});
        } else if (type == "Polygon" || type == "MultiPolygon") {
            geom = j;
        }
    }

    lp.boundary = extract_polygon_coords(geom);
    lp.properties = props;

    if (props.contains("name")) {
        lp.name = props["name"].get<std::string>();
    } else if (props.contains("LAND_ID")) {
        lp.name = props["LAND_ID"].get<std::string>();
    }

    lp.area_sqm = compute_area(lp.boundary);
    return lp;
}

LandParcel GISEngine::parse_geojson_file(const std::string& path) const {
    std::ifstream ifs(path);
    if (!ifs.is_open()) {
        throw std::runtime_error("Cannot open GeoJSON file: " + path);
    }
    std::string content((std::istreambuf_iterator<char>(ifs)),
                         std::istreambuf_iterator<char>());
    return parse_geojson(content);
}

// =========================================================================
// Shapefile Parsing (simplified — reads .shp binary)
// =========================================================================

std::vector<Point2D> GISEngine::parse_shp_polygon(const std::string& path) {
    std::vector<Point2D> pts;
    std::ifstream ifs(path, std::ios::binary);
    if (!ifs.is_open()) return pts;

    // Read file into memory
    std::vector<uint8_t> data((std::istreambuf_iterator<char>(ifs)),
                               std::istreambuf_iterator<char>());
    if (data.size() < 100) return pts; // too small to be a valid SHP

    // Verify magic number (0x0000270a)
    int32_t magic = read_be_int32(&data[0]);
    if (magic != 9994) return pts;

    // Skip to first record (offset 100)
    size_t offset = 100;
    if (offset + 12 > data.size()) return pts;

    // Record header: record number (BE), content length (BE)
    // int32_t rec_num = read_be_int32(&data[offset]);
    // int32_t content_len = read_be_int32(&data[offset + 4]); // in 16-bit words
    offset += 8;

    // Shape type (LE)
    int32_t shape_type = read_le_int32(&data[offset]);
    offset += 4;

    // Polygon shape type = 5
    if (shape_type != 5 && shape_type != 15) return pts;

    // Bounding box (skip 32 bytes: xmin, ymin, xmax, ymax as doubles)
    offset += 32;
    if (offset + 8 > data.size()) return pts;

    int32_t num_parts = read_le_int32(&data[offset]);
    offset += 4;
    int32_t num_points = read_le_int32(&data[offset]);
    offset += 4;

    // Skip parts array (num_parts * 4 bytes)
    offset += static_cast<size_t>(num_parts) * 4;

    // Read points (num_points * 16 bytes: x, y as doubles)
    for (int32_t i = 0; i < num_points && (offset + 16) <= data.size(); ++i) {
        double x = read_le_double(&data[offset]);
        double y = read_le_double(&data[offset + 8]);
        pts.push_back({x, y});
        offset += 16;
    }

    // Remove closing point
    if (pts.size() > 1) {
        const auto& f = pts.front();
        const auto& l = pts.back();
        if (std::abs(f.x - l.x) < 1e-12 && std::abs(f.y - l.y) < 1e-12) {
            pts.pop_back();
        }
    }

    return pts;
}

LandParcel GISEngine::parse_shapefile(const std::string& shp_path) const {
    LandParcel lp;
    lp.boundary = parse_shp_polygon(shp_path);
    lp.area_sqm = compute_area(lp.boundary);
    lp.crs = "unknown"; // would need .prj file to determine
    return lp;
}

// =========================================================================
// DXF Parsing (simplified — LWPOLYLINE entities)
// =========================================================================

LandParcel GISEngine::parse_dxf(const std::string& dxf_path) const {
    LandParcel lp;
    std::ifstream ifs(dxf_path);
    if (!ifs.is_open()) {
        throw std::runtime_error("Cannot open DXF file: " + dxf_path);
    }

    // DXF files consist of group code / value pairs (two lines each).
    // We read them explicitly in pairs.
    std::string code_line, value_line;
    bool in_entities = false;
    bool in_lwpolyline = false;
    double cur_x = 0.0;
    bool have_x = false;
    std::vector<Point2D> current_poly;
    std::vector<Point2D> largest_poly;

    auto trim = [](std::string& s) {
        size_t start = s.find_first_not_of(" \t\r\n");
        if (start == std::string::npos) { s.clear(); return; }
        size_t end = s.find_last_not_of(" \t\r\n");
        s = s.substr(start, end - start + 1);
    };

    while (std::getline(ifs, code_line) && std::getline(ifs, value_line)) {
        trim(code_line);
        trim(value_line);

        int code = 0;
        try { code = std::stoi(code_line); } catch (...) { continue; }

        if (code == 2 && value_line == "ENTITIES") {
            in_entities = true;
            continue;
        }

        if (!in_entities) continue;

        if (code == 0) {
            // Save current polyline if we were in one
            if (in_lwpolyline && current_poly.size() > largest_poly.size()) {
                largest_poly = current_poly;
            }

            if (value_line == "ENDSEC" || value_line == "EOF") break;

            in_lwpolyline = (value_line == "LWPOLYLINE");
            if (in_lwpolyline) {
                current_poly.clear();
                have_x = false;
            }
        } else if (in_lwpolyline) {
            if (code == 10) {
                cur_x = std::stod(value_line);
                have_x = true;
            } else if (code == 20 && have_x) {
                double cur_y = std::stod(value_line);
                current_poly.push_back({cur_x, cur_y});
                have_x = false;
            }
        }
    }

    // Finalize last polyline
    if (in_lwpolyline && current_poly.size() > largest_poly.size()) {
        largest_poly = current_poly;
    }

    lp.boundary = largest_poly;

    lp.area_sqm = compute_area(lp.boundary);
    lp.crs = "unknown";
    return lp;
}

// =========================================================================
// Geometry Operations
// =========================================================================

double GISEngine::compute_area(const std::vector<Point2D>& poly) {
    if (poly.size() < 3) return 0.0;
    double area = 0.0;
    const size_t n = poly.size();
    for (size_t i = 0; i < n; ++i) {
        size_t j = (i + 1) % n;
        area += poly[i].x * poly[j].y - poly[j].x * poly[i].y;
    }
    return std::abs(area) / 2.0;
}

Point2D GISEngine::compute_centroid(const std::vector<Point2D>& poly) {
    if (poly.empty()) return {0.0, 0.0};
    double cx = 0.0, cy = 0.0;
    for (const auto& pt : poly) {
        cx += pt.x;
        cy += pt.y;
    }
    double n = static_cast<double>(poly.size());
    return {cx / n, cy / n};
}

double GISEngine::compute_perimeter(const std::vector<Point2D>& poly) {
    if (poly.size() < 2) return 0.0;
    double perimeter = 0.0;
    const size_t n = poly.size();
    for (size_t i = 0; i < n; ++i) {
        size_t j = (i + 1) % n;
        double dx = poly[j].x - poly[i].x;
        double dy = poly[j].y - poly[i].y;
        perimeter += std::sqrt(dx * dx + dy * dy);
    }
    return perimeter;
}

std::vector<Point2D> GISEngine::apply_setback(
    const std::vector<Point2D>& boundary, double setback_m)
{
    if (boundary.size() < 3 || setback_m <= 0.0) return boundary;

    // Compute centroid
    Point2D c = compute_centroid(boundary);

    // Shrink each vertex toward centroid by setback_m
    std::vector<Point2D> result;
    result.reserve(boundary.size());
    for (const auto& pt : boundary) {
        double dx = pt.x - c.x;
        double dy = pt.y - c.y;
        double dist = std::sqrt(dx * dx + dy * dy);
        if (dist < 1e-12) {
            result.push_back(pt);
            continue;
        }
        double ratio = std::max(0.0, (dist - setback_m) / dist);
        result.push_back({c.x + dx * ratio, c.y + dy * ratio});
    }
    return result;
}

std::vector<Point2D> GISEngine::apply_buffer(
    const std::vector<Point2D>& boundary, double buffer_m)
{
    if (boundary.size() < 3 || buffer_m <= 0.0) return boundary;

    Point2D c = compute_centroid(boundary);

    std::vector<Point2D> result;
    result.reserve(boundary.size());
    for (const auto& pt : boundary) {
        double dx = pt.x - c.x;
        double dy = pt.y - c.y;
        double dist = std::sqrt(dx * dx + dy * dy);
        if (dist < 1e-12) {
            result.push_back(pt);
            continue;
        }
        double ratio = (dist + buffer_m) / dist;
        result.push_back({c.x + dx * ratio, c.y + dy * ratio});
    }
    return result;
}

// =========================================================================
// Coordinate Projection: WGS84 ↔ TWD97 TM2
// =========================================================================

Point2D GISEngine::wgs84_to_twd97(double longitude, double latitude) {
    double lon_rad = longitude * DEG2RAD;
    double lat_rad = latitude * DEG2RAD;
    double lon0_rad = TM2_LON0 * DEG2RAD;

    double sin_lat = std::sin(lat_rad);
    double cos_lat = std::cos(lat_rad);
    double tan_lat = std::tan(lat_rad);

    double N = GRS80_A / std::sqrt(1.0 - GRS80_E2 * sin_lat * sin_lat);
    double T = tan_lat * tan_lat;
    double C = GRS80_EP2 * cos_lat * cos_lat;
    double A = (lon_rad - lon0_rad) * cos_lat;

    // Meridional arc length (M)
    double e2 = GRS80_E2;
    double e4 = e2 * e2;
    double e6 = e4 * e2;
    double M = GRS80_A * (
        (1.0 - e2 / 4.0 - 3.0 * e4 / 64.0 - 5.0 * e6 / 256.0) * lat_rad
      - (3.0 * e2 / 8.0 + 3.0 * e4 / 32.0 + 45.0 * e6 / 1024.0) * std::sin(2.0 * lat_rad)
      + (15.0 * e4 / 256.0 + 45.0 * e6 / 1024.0) * std::sin(4.0 * lat_rad)
      - (35.0 * e6 / 3072.0) * std::sin(6.0 * lat_rad)
    );

    double A2 = A * A;
    double A3 = A2 * A;
    double A4 = A2 * A2;
    double A5 = A4 * A;
    double A6 = A3 * A3;

    double easting = TM2_FE + TM2_K0 * N * (
        A + (1.0 - T + C) * A3 / 6.0
        + (5.0 - 18.0 * T + T * T + 72.0 * C - 58.0 * GRS80_EP2) * A5 / 120.0
    );

    double northing = TM2_FN + TM2_K0 * (
        M + N * tan_lat * (
            A2 / 2.0
            + (5.0 - T + 9.0 * C + 4.0 * C * C) * A4 / 24.0
            + (61.0 - 58.0 * T + T * T + 600.0 * C - 330.0 * GRS80_EP2) * A6 / 720.0
        )
    );

    return {easting, northing};
}

Point2D GISEngine::twd97_to_wgs84(double easting, double northing) {
    double x = easting - TM2_FE;
    double y = northing - TM2_FN;

    double M = y / TM2_K0;

    double e2 = GRS80_E2;
    double e4 = e2 * e2;
    double e6 = e4 * e2;
    double e1 = (1.0 - std::sqrt(1.0 - e2)) / (1.0 + std::sqrt(1.0 - e2));

    double mu = M / (GRS80_A * (1.0 - e2 / 4.0 - 3.0 * e4 / 64.0 - 5.0 * e6 / 256.0));

    double phi1 = mu
        + (3.0 * e1 / 2.0 - 27.0 * e1 * e1 * e1 / 32.0) * std::sin(2.0 * mu)
        + (21.0 * e1 * e1 / 16.0 - 55.0 * e1 * e1 * e1 * e1 / 32.0) * std::sin(4.0 * mu)
        + (151.0 * e1 * e1 * e1 / 96.0) * std::sin(6.0 * mu);

    double sin_phi = std::sin(phi1);
    double cos_phi = std::cos(phi1);
    double tan_phi = std::tan(phi1);

    double N1 = GRS80_A / std::sqrt(1.0 - e2 * sin_phi * sin_phi);
    double T1 = tan_phi * tan_phi;
    double C1 = GRS80_EP2 * cos_phi * cos_phi;
    double R1 = GRS80_A * (1.0 - e2) /
                std::pow(1.0 - e2 * sin_phi * sin_phi, 1.5);
    double D = x / (N1 * TM2_K0);
    double D2 = D * D;
    double D3 = D2 * D;
    double D4 = D2 * D2;
    double D5 = D4 * D;
    double D6 = D3 * D3;

    double lat_rad = phi1 - (N1 * tan_phi / R1) * (
        D2 / 2.0
        - (5.0 + 3.0 * T1 + 10.0 * C1 - 4.0 * C1 * C1 - 9.0 * GRS80_EP2) * D4 / 24.0
        + (61.0 + 90.0 * T1 + 298.0 * C1 + 45.0 * T1 * T1
           - 252.0 * GRS80_EP2 - 3.0 * C1 * C1) * D6 / 720.0
    );

    double lon_rad = TM2_LON0 * DEG2RAD + (
        D - (1.0 + 2.0 * T1 + C1) * D3 / 6.0
        + (5.0 - 2.0 * C1 + 28.0 * T1 - 3.0 * C1 * C1
           + 8.0 * GRS80_EP2 + 24.0 * T1 * T1) * D5 / 120.0
    ) / cos_phi;

    return {lon_rad * RAD2DEG, lat_rad * RAD2DEG};
}

std::vector<Point2D> GISEngine::project_boundary_to_twd97(
    const std::vector<Point2D>& wgs84_pts)
{
    std::vector<Point2D> result;
    result.reserve(wgs84_pts.size());
    for (const auto& pt : wgs84_pts) {
        result.push_back(wgs84_to_twd97(pt.x, pt.y));
    }
    return result;
}

// =========================================================================
// C ABI Implementation
// =========================================================================

} // namespace promptbim

// --- C ABI functions (replace stubs in future_stubs.cpp) ---

struct PBLandParcel {
    promptbim::LandParcel inner;
};

PBLandParcel* pb_land_from_geojson(const char* path) {
    try {
        promptbim::GISEngine engine;
        auto lp = engine.parse_geojson_file(path);
        auto* result = new PBLandParcel{std::move(lp)};
        return result;
    } catch (...) {
        return nullptr;
    }
}

PBLandParcel* pb_land_from_shapefile(const char* path) {
    try {
        promptbim::GISEngine engine;
        auto lp = engine.parse_shapefile(path);
        auto* result = new PBLandParcel{std::move(lp)};
        return result;
    } catch (...) {
        return nullptr;
    }
}

PBLandParcel* pb_land_from_dxf(const char* path) {
    try {
        promptbim::GISEngine engine;
        auto lp = engine.parse_dxf(path);
        auto* result = new PBLandParcel{std::move(lp)};
        return result;
    } catch (...) {
        return nullptr;
    }
}

void pb_land_free(PBLandParcel* parcel) {
    delete parcel;
}

char* pb_land_to_json(const PBLandParcel* parcel) {
    if (!parcel) return nullptr;
    try {
        std::string s = parcel->inner.to_json().dump();
        char* buf = static_cast<char*>(std::malloc(s.size() + 1));
        if (buf) {
            std::memcpy(buf, s.c_str(), s.size() + 1);
        }
        return buf;
    } catch (...) {
        return nullptr;
    }
}

PBLandParcel* pb_land_from_geojson_string(const char* geojson_str) {
    if (!geojson_str) return nullptr;
    try {
        promptbim::GISEngine engine;
        auto lp = engine.parse_geojson(geojson_str);
        return new PBLandParcel{std::move(lp)};
    } catch (...) {
        return nullptr;
    }
}
