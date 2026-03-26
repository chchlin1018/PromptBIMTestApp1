/**
 * mep_engine.cpp — MEP A* Pathfinding Engine (C++)
 *
 * Ports src/promptbim/bim/mep/pathfinder.py to C++17.
 * Features:
 *   - 3D voxel grid with configurable resolution
 *   - 6-directional orthogonal A* with turn penalty
 *   - Path simplification (collinear removal)
 *   - Obstacle management (manual, bbox, wall-based)
 *   - C ABI via pb_plan_mep()
 */

#include "promptbim/mep_engine.hpp"
#include "promptbim/promptbim.h"

#include <algorithm>
#include <cmath>
#include <cstring>
#include <functional>
#include <limits>

namespace promptbim {

// -----------------------------------------------------------------------
// 6-directional movement (orthogonal only)
// -----------------------------------------------------------------------

static const int DIRS[6][3] = {
    { 1, 0, 0}, {-1, 0, 0},
    { 0, 1, 0}, { 0,-1, 0},
    { 0, 0, 1}, { 0, 0,-1},
};

// -----------------------------------------------------------------------
// Construction
// -----------------------------------------------------------------------

MEPEngine::MEPEngine(double grid_size)
    : grid_size_(grid_size > 0.0 ? grid_size : 0.3)
{}

// -----------------------------------------------------------------------
// Obstacle management
// -----------------------------------------------------------------------

void MEPEngine::add_obstacle(int gx, int gy, int gz) {
    obstacles_.insert({gx, gy, gz});
}

void MEPEngine::add_obstacles_from_bbox(const Point3D& min_pt,
                                          const Point3D& max_pt) {
    GridPoint gmin = to_grid(min_pt);
    GridPoint gmax = to_grid(max_pt);
    // Ensure min <= max
    int x0 = std::min(gmin.gx, gmax.gx), x1 = std::max(gmin.gx, gmax.gx);
    int y0 = std::min(gmin.gy, gmax.gy), y1 = std::max(gmin.gy, gmax.gy);
    int z0 = std::min(gmin.gz, gmax.gz), z1 = std::max(gmin.gz, gmax.gz);
    for (int x = x0; x <= x1; ++x)
        for (int y = y0; y <= y1; ++y)
            for (int z = z0; z <= z1; ++z)
                obstacles_.insert({x, y, z});
}

void MEPEngine::add_obstacles_from_walls(const nlohmann::json& walls,
                                           double elevation,
                                           double height) {
    if (!walls.is_array()) return;
    for (const auto& wall : walls) {
        if (!wall.contains("start") || !wall.contains("end")) continue;
        double sx = wall["start"][0].get<double>();
        double sy = wall["start"][1].get<double>();
        double ex = wall["end"][0].get<double>();
        double ey = wall["end"][1].get<double>();
        double thickness = wall.value("thickness_m", 0.2);
        double half_t = thickness / 2.0;

        // Compute perpendicular offset for wall bounding box
        double dx = ex - sx, dy = ey - sy;
        double len = std::sqrt(dx * dx + dy * dy);
        if (len < 1e-9) continue;
        double nx = -dy / len * half_t;
        double ny =  dx / len * half_t;

        double x_coords[] = {sx + nx, sx - nx, ex + nx, ex - nx};
        double y_coords[] = {sy + ny, sy - ny, ey + ny, ey - ny};

        double xmin = *std::min_element(x_coords, x_coords + 4);
        double xmax = *std::max_element(x_coords, x_coords + 4);
        double ymin = *std::min_element(y_coords, y_coords + 4);
        double ymax = *std::max_element(y_coords, y_coords + 4);

        add_obstacles_from_bbox(
            {xmin, ymin, elevation},
            {xmax, ymax, elevation + height}
        );
    }
}

void MEPEngine::clear_obstacles() {
    obstacles_.clear();
}

// -----------------------------------------------------------------------
// Grid conversion
// -----------------------------------------------------------------------

GridPoint MEPEngine::to_grid(const Point3D& p) const {
    return {
        static_cast<int>(std::round(p.x / grid_size_)),
        static_cast<int>(std::round(p.y / grid_size_)),
        static_cast<int>(std::round(p.z / grid_size_)),
    };
}

Point3D MEPEngine::to_world(const GridPoint& g) const {
    return {
        g.gx * grid_size_,
        g.gy * grid_size_,
        g.gz * grid_size_,
    };
}

// -----------------------------------------------------------------------
// A* Pathfinding
// -----------------------------------------------------------------------

RoutePath MEPEngine::find_path(const Point3D& start_pt, const Point3D& end_pt,
                                double turn_penalty, int max_iterations) const
{
    GridPoint start_g = to_grid(start_pt);
    GridPoint end_g   = to_grid(end_pt);

    // Same start/end → trivial path
    if (start_g == end_g) {
        Point3D w = to_world(start_g);
        return {{w}, {}, 0.0};
    }

    // If goal is an obstacle → no path
    if (obstacles_.count(end_g)) return {{}, {}, 0.0};

    // Heuristic: Manhattan distance scaled by grid_size
    auto heuristic = [&](const GridPoint& a) -> double {
        return (std::abs(a.gx - end_g.gx) +
                std::abs(a.gy - end_g.gy) +
                std::abs(a.gz - end_g.gz)) * grid_size_;
    };

    // Open set: (f_cost, counter, position, prev_direction_index)
    // prev_direction_index: -1 = start (no prev direction)
    struct Node {
        double f_cost;
        int counter;
        GridPoint pos;
        int prev_dir;
        bool operator>(const Node& o) const { return f_cost > o.f_cost; }
    };

    std::priority_queue<Node, std::vector<Node>, std::greater<Node>> open;
    std::unordered_map<GridPoint, double, GridPointHash> g_score;
    std::unordered_map<GridPoint, GridPoint, GridPointHash> came_from;

    g_score[start_g] = 0.0;
    open.push({heuristic(start_g), 0, start_g, -1});
    int counter = 1;
    int iterations = 0;

    bool found = false;

    while (!open.empty() && iterations < max_iterations) {
        ++iterations;
        auto current = open.top();
        open.pop();

        if (current.pos == end_g) {
            found = true;
            break;
        }

        // Skip if we already found a better path to this node
        auto git = g_score.find(current.pos);
        if (git != g_score.end() && current.f_cost - heuristic(current.pos) > git->second + 1e-9)
            continue;

        for (int d = 0; d < 6; ++d) {
            GridPoint neighbor = {
                current.pos.gx + DIRS[d][0],
                current.pos.gy + DIRS[d][1],
                current.pos.gz + DIRS[d][2],
            };

            if (obstacles_.count(neighbor)) continue;

            double move_cost = grid_size_;
            // Turn penalty: add if direction changed from previous
            if (current.prev_dir >= 0 && current.prev_dir != d) {
                move_cost += turn_penalty;
            }

            double tentative_g = g_score[current.pos] + move_cost;
            auto nit = g_score.find(neighbor);
            if (nit == g_score.end() || tentative_g < nit->second) {
                g_score[neighbor] = tentative_g;
                came_from[neighbor] = current.pos;
                double f = tentative_g + heuristic(neighbor);
                open.push({f, counter++, neighbor, d});
            }
        }
    }

    if (!found) return {{}, {}, 0.0};

    // Reconstruct path
    std::vector<GridPoint> grid_path;
    GridPoint cur = end_g;
    while (!(cur == start_g)) {
        grid_path.push_back(cur);
        cur = came_from[cur];
    }
    grid_path.push_back(start_g);
    std::reverse(grid_path.begin(), grid_path.end());

    // Convert to world coordinates
    std::vector<Point3D> raw_waypoints;
    raw_waypoints.reserve(grid_path.size());
    for (const auto& gp : grid_path)
        raw_waypoints.push_back(to_world(gp));

    // Simplify collinear points
    auto waypoints = simplify_path(raw_waypoints);
    auto segments  = build_segments(waypoints);

    double total = 0.0;
    for (const auto& s : segments) total += s.length_m;

    return {waypoints, segments, total};
}

// -----------------------------------------------------------------------
// Path simplification
// -----------------------------------------------------------------------

std::vector<Point3D> MEPEngine::simplify_path(const std::vector<Point3D>& path) {
    if (path.size() <= 2) return path;

    std::vector<Point3D> result;
    result.push_back(path[0]);

    for (size_t i = 1; i + 1 < path.size(); ++i) {
        // Check if direction from i-1 to i equals direction from i to i+1
        double dx1 = path[i].x - path[i-1].x;
        double dy1 = path[i].y - path[i-1].y;
        double dz1 = path[i].z - path[i-1].z;
        double dx2 = path[i+1].x - path[i].x;
        double dy2 = path[i+1].y - path[i].y;
        double dz2 = path[i+1].z - path[i].z;

        // Normalize
        double len1 = std::sqrt(dx1*dx1 + dy1*dy1 + dz1*dz1);
        double len2 = std::sqrt(dx2*dx2 + dy2*dy2 + dz2*dz2);
        if (len1 < 1e-9 || len2 < 1e-9) continue;

        dx1 /= len1; dy1 /= len1; dz1 /= len1;
        dx2 /= len2; dy2 /= len2; dz2 /= len2;

        // If directions differ, keep this point
        if (std::abs(dx1 - dx2) > 1e-6 ||
            std::abs(dy1 - dy2) > 1e-6 ||
            std::abs(dz1 - dz2) > 1e-6) {
            result.push_back(path[i]);
        }
    }

    result.push_back(path.back());
    return result;
}

std::vector<PathSegment> MEPEngine::build_segments(const std::vector<Point3D>& waypoints) {
    std::vector<PathSegment> segments;
    if (waypoints.size() < 2) return segments;

    for (size_t i = 0; i + 1 < waypoints.size(); ++i) {
        PathSegment seg;
        seg.start = waypoints[i];
        seg.end   = waypoints[i + 1];

        double ddx = seg.end.x - seg.start.x;
        double ddy = seg.end.y - seg.start.y;
        double ddz = seg.end.z - seg.start.z;

        seg.length_m = std::sqrt(ddx*ddx + ddy*ddy + ddz*ddz);

        // Direction as unit integers (since we move orthogonally)
        if (std::abs(ddx) > 1e-9) seg.dx = (ddx > 0) ? 1 : -1;
        if (std::abs(ddy) > 1e-9) seg.dy = (ddy > 0) ? 1 : -1;
        if (std::abs(ddz) > 1e-9) seg.dz = (ddz > 0) ? 1 : -1;

        segments.push_back(seg);
    }
    return segments;
}

// -----------------------------------------------------------------------
// JSON interface: plan_mep
// -----------------------------------------------------------------------

std::string MEPEngine::plan_mep(const std::string& plan_json,
                                  const std::string& config_json) const
{
    nlohmann::json plan, config;
    try {
        plan = nlohmann::json::parse(plan_json);
        if (!config_json.empty())
            config = nlohmann::json::parse(config_json);
    } catch (const nlohmann::json::exception& e) {
        return nlohmann::json{{"error", std::string("JSON parse error: ") + e.what()}}.dump();
    }

    double grid = config.value("grid_size", grid_size_);
    double penalty = config.value("turn_penalty", 2.0);
    int max_iter = config.value("max_iterations", 50000);

    MEPEngine engine(grid);

    // Load obstacles from wall geometry
    if (plan.contains("stories")) {
        for (const auto& story : plan["stories"]) {
            double elev = story.value("elevation_m", 0.0);
            double h_m  = story.value("height_m", 3.0);
            if (story.contains("walls")) {
                engine.add_obstacles_from_walls(story["walls"], elev, h_m);
            }
        }
    }

    // Route MEP for each story: equipment (riser) → terminals
    nlohmann::json routes = nlohmann::json::array();
    nlohmann::json equipment_list = nlohmann::json::array();

    if (plan.contains("stories") && plan.contains("building_footprint")) {
        const auto& fp = plan["building_footprint"];
        // Find centroid for riser position
        double cx = 0.0, cy = 0.0;
        if (fp.is_array() && fp.size() >= 3) {
            for (const auto& pt : fp) {
                cx += pt[0].get<double>();
                cy += pt[1].get<double>();
            }
            cx /= fp.size();
            cy /= fp.size();
        }

        for (const auto& story : plan["stories"]) {
            double elev = story.value("elevation_m", 0.0);
            double h_m  = story.value("height_m", 3.0);
            double z_ceiling = elev + h_m - 0.3; // route near ceiling
            std::string sn = story.value("name", "");

            // Equipment: riser at centroid near ceiling
            Point3D riser_pos = {cx, cy, z_ceiling};
            equipment_list.push_back({
                {"system", "plumbing"},
                {"position", riser_pos.to_json()},
                {"floor", sn},
            });

            // Route to each space centroid
            if (story.contains("spaces")) {
                for (const auto& sp : story["spaces"]) {
                    if (!sp.contains("boundary") || !sp["boundary"].is_array()) continue;
                    const auto& bnd = sp["boundary"];
                    if (bnd.size() < 3) continue;

                    double scx = 0.0, scy = 0.0;
                    for (const auto& pt : bnd) {
                        scx += pt[0].get<double>();
                        scy += pt[1].get<double>();
                    }
                    scx /= bnd.size();
                    scy /= bnd.size();

                    Point3D terminal_pos = {scx, scy, z_ceiling};
                    auto path = engine.find_path(riser_pos, terminal_pos,
                                                  penalty, max_iter);
                    if (!path.waypoints.empty()) {
                        routes.push_back({
                            {"system", "plumbing"},
                            {"floor", sn},
                            {"space", sp.value("name", "")},
                            {"path", path.to_json()},
                        });
                    }
                }
            }
        }
    }

    nlohmann::json out = {
        {"routes", routes},
        {"equipment", equipment_list},
        {"grid_size", grid},
        {"turn_penalty", penalty},
    };
    return out.dump();
}

} // namespace promptbim

// -----------------------------------------------------------------------
// C ABI — replaces placeholder in compliance_engine.cpp
// -----------------------------------------------------------------------

char* pb_plan_mep(const char* plan_json, const char* config_json) {
    if (!plan_json) return nullptr;
    try {
        promptbim::MEPEngine engine;
        std::string cfg = config_json ? config_json : "";
        std::string result = engine.plan_mep(plan_json, cfg);
        char* out = static_cast<char*>(std::malloc(result.size() + 1));
        if (!out) return nullptr;
        std::memcpy(out, result.data(), result.size() + 1);
        return out;
    } catch (...) {
        return nullptr;
    }
}
