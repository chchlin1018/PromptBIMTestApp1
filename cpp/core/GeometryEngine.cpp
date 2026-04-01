#include "GeometryEngine.h"
#include <cmath>
#include <numbers>
#include <algorithm>

namespace bim {

AABB::AABB(const Vec3& center, const Vec3& dims) noexcept {
    Vec3 half{std::abs(dims.x) / 2.0, std::abs(dims.y) / 2.0, std::abs(dims.z) / 2.0};
    min = center - half;
    max = center + half;
}

bool AABB::intersects(const AABB& other) const noexcept {
    return min.x <= other.max.x && max.x >= other.min.x &&
           min.y <= other.max.y && max.y >= other.min.y &&
           min.z <= other.max.z && max.z >= other.min.z;
}

double AABB::volume() const noexcept {
    return (max.x - min.x) * (max.y - min.y) * (max.z - min.z);
}

double AABB::surfaceArea() const noexcept {
    double w = max.x - min.x, h = max.y - min.y, d = max.z - min.z;
    return 2.0 * (w * h + h * d + w * d);
}

Vec3 AABB::center() const noexcept {
    return {(min.x + max.x) / 2.0, (min.y + max.y) / 2.0, (min.z + max.z) / 2.0};
}

double GeometryEngine::polygonArea(const std::vector<Vec3>& vertices) {
    if (vertices.size() < 3) return 0.0;
    double area = 0.0;
    size_t n = vertices.size();
    for (size_t i = 0; i < n; ++i) {
        const auto& a = vertices[i];
        const auto& b = vertices[(i + 1) % n];
        area += a.x * b.y - b.x * a.y;
    }
    return std::abs(area) / 2.0;
}

Vec3 GeometryEngine::polygonCentroid(const std::vector<Vec3>& vertices) {
    if (vertices.empty()) return {};
    double cx = 0.0, cy = 0.0, cz = 0.0;
    for (const auto& v : vertices) { cx += v.x; cy += v.y; cz += v.z; }
    double n = static_cast<double>(vertices.size());
    return {cx / n, cy / n, cz / n};
}

double GeometryEngine::polygonPerimeter(const std::vector<Vec3>& vertices) {
    if (vertices.size() < 2) return 0.0;
    double perimeter = 0.0;
    for (size_t i = 0; i < vertices.size(); ++i) {
        perimeter += vertices[i].distanceTo(vertices[(i + 1) % vertices.size()]);
    }
    return perimeter;
}

double GeometryEngine::boxVolume(const Vec3& d) noexcept {
    return std::abs(d.x * d.y * d.z);
}

double GeometryEngine::cylinderVolume(double radius, double height) noexcept {
    return std::numbers::pi * radius * radius * std::abs(height);
}

double GeometryEngine::sphereVolume(double radius) noexcept {
    return (4.0 / 3.0) * std::numbers::pi * radius * radius * radius;
}

double GeometryEngine::boxSurfaceArea(const Vec3& d) noexcept {
    double w = std::abs(d.x), h = std::abs(d.y), depth = std::abs(d.z);
    return 2.0 * (w * h + h * depth + w * depth);
}

double GeometryEngine::cylinderSurfaceArea(double radius, double height) noexcept {
    return 2.0 * std::numbers::pi * radius * (radius + std::abs(height));
}

bool GeometryEngine::checkCollision(const Vec3& pos1, const Vec3& dims1,
                                     const Vec3& pos2, const Vec3& dims2) noexcept {
    AABB a(pos1, dims1), b(pos2, dims2);
    return a.intersects(b);
}

std::vector<std::pair<std::string, std::string>>
GeometryEngine::detectCollisions(const std::vector<std::tuple<std::string, Vec3, Vec3>>& entities) {
    std::vector<std::pair<std::string, std::string>> collisions;
    for (size_t i = 0; i < entities.size(); ++i) {
        for (size_t j = i + 1; j < entities.size(); ++j) {
            const auto& [id1, pos1, dims1] = entities[i];
            const auto& [id2, pos2, dims2] = entities[j];
            if (checkCollision(pos1, dims1, pos2, dims2)) {
                collisions.emplace_back(id1, id2);
            }
        }
    }
    return collisions;
}

double GeometryEngine::pointToLineDistance(const Vec3& point, const Vec3& lineStart, const Vec3& lineEnd) {
    Vec3 d = lineEnd - lineStart;
    double len2 = d.dot(d);
    if (len2 < 1e-10) return point.distanceTo(lineStart);
    double t = std::clamp((point - lineStart).dot(d) / len2, 0.0, 1.0);
    Vec3 proj = lineStart + d * t;
    return point.distanceTo(proj);
}

double GeometryEngine::entityDistance(const Vec3& pos1, const Vec3& pos2) noexcept {
    return pos1.distanceTo(pos2);
}

} // namespace bim
