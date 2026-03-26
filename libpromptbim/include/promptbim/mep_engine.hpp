/**
 * mep_engine.hpp — MEP A* Pathfinding Engine (C++)
 *
 * Ports src/promptbim/bim/mep/pathfinder.py A* algorithm to C++17.
 * Voxel-based 3D grid with 6-directional orthogonal movement + turn penalty.
 */

#pragma once

#include <nlohmann/json.hpp>
#include <cmath>
#include <queue>
#include <set>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace promptbim {

// -----------------------------------------------------------------------
// Data structures
// -----------------------------------------------------------------------

struct Point3D {
    double x = 0.0, y = 0.0, z = 0.0;
    nlohmann::json to_json() const {
        return nlohmann::json::array({x, y, z});
    }
};

struct GridPoint {
    int gx = 0, gy = 0, gz = 0;
    bool operator==(const GridPoint& o) const {
        return gx == o.gx && gy == o.gy && gz == o.gz;
    }
};

struct GridPointHash {
    std::size_t operator()(const GridPoint& p) const {
        auto h1 = std::hash<int>()(p.gx);
        auto h2 = std::hash<int>()(p.gy);
        auto h3 = std::hash<int>()(p.gz);
        return h1 ^ (h2 << 16) ^ (h3 << 8);
    }
};

struct PathSegment {
    Point3D start, end;
    int dx = 0, dy = 0, dz = 0;
    double length_m = 0.0;

    nlohmann::json to_json() const {
        return {
            {"start", start.to_json()},
            {"end", end.to_json()},
            {"direction", nlohmann::json::array({dx, dy, dz})},
            {"length_m", length_m},
        };
    }
};

struct RoutePath {
    std::vector<Point3D> waypoints;
    std::vector<PathSegment> segments;
    double total_length_m = 0.0;

    nlohmann::json to_json() const {
        nlohmann::json wp = nlohmann::json::array();
        for (const auto& p : waypoints) wp.push_back(p.to_json());
        nlohmann::json sg = nlohmann::json::array();
        for (const auto& s : segments) sg.push_back(s.to_json());
        return {
            {"waypoints", wp},
            {"segments", sg},
            {"total_length_m", total_length_m},
        };
    }
};

// -----------------------------------------------------------------------
// MEPEngine — A* pathfinder with voxel obstacles
// -----------------------------------------------------------------------

class MEPEngine {
public:
    explicit MEPEngine(double grid_size = 0.3);

    // Obstacle management
    void add_obstacle(int gx, int gy, int gz);
    void add_obstacles_from_bbox(const Point3D& min_pt, const Point3D& max_pt);
    void add_obstacles_from_walls(const nlohmann::json& walls,
                                   double elevation, double height);
    void clear_obstacles();
    std::size_t obstacle_count() const { return obstacles_.size(); }

    // A* pathfinding
    RoutePath find_path(const Point3D& start, const Point3D& end,
                        double turn_penalty = 2.0,
                        int max_iterations = 50000) const;

    // Grid conversion
    GridPoint to_grid(const Point3D& p) const;
    Point3D   to_world(const GridPoint& g) const;

    double grid_size() const { return grid_size_; }

    // JSON interface (for C ABI)
    std::string plan_mep(const std::string& plan_json,
                          const std::string& config_json) const;

private:
    double grid_size_;
    std::unordered_set<GridPoint, GridPointHash> obstacles_;

    // Path simplification: remove collinear intermediate points
    static std::vector<Point3D> simplify_path(const std::vector<Point3D>& path);
    // Build segments from simplified waypoints
    static std::vector<PathSegment> build_segments(const std::vector<Point3D>& waypoints);
};

} // namespace promptbim
