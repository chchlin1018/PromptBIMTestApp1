#pragma once
// GeometryEngine.h — Basic geometry calculations (area/volume/collision)

#include "BIMTypes.h"
#include <vector>

namespace bim {

struct AABB {
    Vec3 min, max;
    AABB() = default;
    AABB(const Vec3& center, const Vec3& dims);
    bool intersects(const AABB& other) const;
    double volume() const;
    double surfaceArea() const;
    Vec3 center() const;
};

class GeometryEngine {
public:
    // Polygon operations
    static double polygonArea(const std::vector<Vec3>& vertices);
    static Vec3 polygonCentroid(const std::vector<Vec3>& vertices);
    static double polygonPerimeter(const std::vector<Vec3>& vertices);

    // Volume calculations
    static double boxVolume(const Vec3& dimensions);
    static double cylinderVolume(double radius, double height);
    static double sphereVolume(double radius);

    // Surface area
    static double boxSurfaceArea(const Vec3& dimensions);
    static double cylinderSurfaceArea(double radius, double height);

    // Collision detection (AABB)
    static bool checkCollision(const Vec3& pos1, const Vec3& dims1,
                                const Vec3& pos2, const Vec3& dims2);
    static std::vector<std::pair<std::string, std::string>>
        detectCollisions(const std::vector<std::tuple<std::string, Vec3, Vec3>>& entities);

    // Distance
    static double pointToLineDistance(const Vec3& point, const Vec3& lineStart, const Vec3& lineEnd);
    static double entityDistance(const Vec3& pos1, const Vec3& pos2);
};

} // namespace bim
