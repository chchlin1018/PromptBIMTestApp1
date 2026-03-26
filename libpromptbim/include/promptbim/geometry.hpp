/**
 * geometry.hpp — Shared geometry utilities for libpromptbim
 *
 * Common geometric functions used by multiple engines.
 * Extracted from compliance_engine.cpp and cost_engine.cpp (P18 tech debt).
 */

#pragma once

#include <nlohmann/json.hpp>

namespace promptbim {
namespace geometry {

/**
 * Compute polygon area using the Shoelace formula.
 * @param coords JSON array of [[x,y], ...] coordinates
 * @return Absolute area (always >= 0)
 */
double poly_area(const nlohmann::json& coords);

/**
 * Compute centroid of a polygon.
 * @param coords JSON array of [[x,y], ...] coordinates
 * @return {x, y} centroid as pair
 */
std::pair<double, double> poly_centroid(const nlohmann::json& coords);

/**
 * Compute wall length from wall JSON object.
 * @param wall JSON with "start" and "end" as [x,y] arrays
 * @return Euclidean distance
 */
double wall_length(const nlohmann::json& wall);

} // namespace geometry
} // namespace promptbim
