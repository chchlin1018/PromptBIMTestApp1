#pragma once
// GeometryEngine.h — Basic geometry calculations (area/volume/collision)

#include "BIMTypes.h"
#include <vector>

namespace bim {

struct AABB {
    Vec3 min, max;
    AABB() noexcept = default;
    AABB(const Vec3& center, const Vec3& dims) noexcept;
    [[nodiscard]] bool intersects(const AABB& other) const noexcept;
    [[nodiscard]] double volume() const noexcept;
    [[nodiscard]] double surfaceArea() const noexcept;
    [[nodiscard]] Vec3 center() const noexcept;
};

class GeometryEngine {
public:
    // Polygon operations
    [[nodiscard]] static double polygonArea(const std::vector<Vec3>& vertices);
    [[nodiscard]] static Vec3 polygonCentroid(const std::vector<Vec3>& vertices);
    [[nodiscard]] static double polygonPerimeter(const std::vector<Vec3>& vertices);

    // Volume calculations
    [[nodiscard]] static double boxVolume(const Vec3& dimensions) noexcept;
    [[nodiscard]] static double cylinderVolume(double radius, double height) noexcept;
    [[nodiscard]] static double sphereVolume(double radius) noexcept;

    // Surface area
    [[nodiscard]] static double boxSurfaceArea(const Vec3& dimensions) noexcept;
    [[nodiscard]] static double cylinderSurfaceArea(double radius, double height) noexcept;

    // Collision detection (AABB)
    [[nodiscard]] static bool checkCollision(const Vec3& pos1, const Vec3& dims1,
                                              const Vec3& pos2, const Vec3& dims2) noexcept;
    [[nodiscard]] static std::vector<std::pair<std::string, std::string>>
        detectCollisions(const std::vector<std::tuple<std::string, Vec3, Vec3>>& entities);

    // Distance
    [[nodiscard]] static double pointToLineDistance(const Vec3& point, const Vec3& lineStart, const Vec3& lineEnd);
    [[nodiscard]] static double entityDistance(const Vec3& pos1, const Vec3& pos2) noexcept;
};

} // namespace bim
