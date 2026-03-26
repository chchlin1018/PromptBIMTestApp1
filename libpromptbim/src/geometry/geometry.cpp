/**
 * geometry.cpp — Shared geometry utilities
 *
 * Extracted from compliance_engine.cpp and cost_engine.cpp to eliminate
 * duplicate poly_area() implementations (P18 tech debt).
 */

#include "promptbim/geometry.hpp"
#include <cmath>

namespace promptbim {
namespace geometry {

double poly_area(const nlohmann::json& coords) {
    if (!coords.is_array() || coords.size() < 3) return 0.0;
    double area = 0.0;
    const size_t n = coords.size();
    for (size_t i = 0; i < n; ++i) {
        size_t j = (i + 1) % n;
        double xi = coords[i][0].get<double>();
        double yi = coords[i][1].get<double>();
        double xj = coords[j][0].get<double>();
        double yj = coords[j][1].get<double>();
        area += xi * yj - xj * yi;
    }
    return std::abs(area) / 2.0;
}

std::pair<double, double> poly_centroid(const nlohmann::json& coords) {
    if (!coords.is_array() || coords.empty()) return {0.0, 0.0};
    double cx = 0.0, cy = 0.0;
    const size_t n = coords.size();
    for (size_t i = 0; i < n; ++i) {
        cx += coords[i][0].get<double>();
        cy += coords[i][1].get<double>();
    }
    return {cx / n, cy / n};
}

double wall_length(const nlohmann::json& wall) {
    if (!wall.contains("start") || !wall.contains("end")) return 0.0;
    double dx = wall["end"][0].get<double>() - wall["start"][0].get<double>();
    double dy = wall["end"][1].get<double>() - wall["start"][1].get<double>();
    return std::sqrt(dx * dx + dy * dy);
}

} // namespace geometry
} // namespace promptbim
