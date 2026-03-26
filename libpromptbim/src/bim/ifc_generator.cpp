/**
 * ifc_generator.cpp — IFC4 SPF (STEP Physical File) generator
 *
 * Writes valid IFC4 text files directly, matching the output structure
 * of the Python IFCGenerator (which uses ifcopenshell.api.run()).
 *
 * IFC-SPF format reference: ISO 10303-21 / ISO 16739-1:2018
 *
 * Phase 3: V2 Migration — Sprint P20
 */

#include "promptbim/ifc_generator.hpp"
#include "promptbim/promptbim.h"

#include <cmath>
#include <cstring>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <limits>
#include <sstream>

namespace promptbim {

// -------------------------------------------------------------------------
// Construction / Reset
// -------------------------------------------------------------------------

IFCGenerator::IFCGenerator() : next_id_(0) {}

void IFCGenerator::reset() {
    next_id_ = 0;
    entities_.clear();
    material_cache_.clear();
}

// -------------------------------------------------------------------------
// Entity management
// -------------------------------------------------------------------------

int IFCGenerator::add_entity(const std::string& type, const std::string& args) {
    if (next_id_ >= std::numeric_limits<int>::max() - 1) {
        return -1;  // overflow protection
    }
    int id = ++next_id_;
    entities_.push_back({id, type, args});
    return id;
}

namespace {
bool is_valid_coord(double v) {
    return std::isfinite(v);
}
} // anonymous namespace

// -------------------------------------------------------------------------
// Public API
// -------------------------------------------------------------------------

int IFCGenerator::generate(const std::string& plan_json,
                           const std::string& output_path) {
    std::string content = generate_string(plan_json);
    if (content.empty()) return -1;

    std::ofstream ofs(output_path);
    if (!ofs.is_open()) return -1;
    ofs << content;
    ofs.close();
    return 0;
}

std::string IFCGenerator::generate_string(const std::string& plan_json) {
    std::lock_guard<std::mutex> lock(mutex_);
    reset();

    nlohmann::json plan;
    try {
        plan = nlohmann::json::parse(plan_json);
    } catch (...) {
        return "";
    }

    std::string name = plan.value("name", "PromptBIM Building");

    // Create IFC structure
    int units_id = create_units();
    int context_id = create_geometric_context();
    int project_id = create_project(name);
    int site_id = create_site(project_id);
    int building_id = create_building(site_id, name);

    // Process stories
    auto& stories = plan["stories"];
    std::vector<int> storey_ids;

    if (stories.is_array()) {
        for (auto& story : stories) {
            std::string sname = story.value("name", "Story");
            double elevation = story.value("elevation_m", 0.0);
            double height = story.value("height_m", 3.0);
            int storey_id = create_storey(building_id, sname, elevation);
            storey_ids.push_back(storey_id);

            std::vector<int> elements;

            // Walls
            if (story.contains("walls") && story["walls"].is_array()) {
                for (auto& wall : story["walls"]) {
                    auto& s = wall["start"];
                    auto& e = wall["end"];
                    double sx = s[0].get<double>();
                    double sy = s[1].get<double>();
                    double ex = e[0].get<double>();
                    double ey = e[1].get<double>();
                    double thick = wall.value("thickness_m", 0.2);
                    std::string wtype = wall.value("wall_type", "exterior");
                    int wid = create_wall(storey_id, context_id,
                                          sx, sy, ex, ey,
                                          elevation, height, thick, wtype);
                    elements.push_back(wid);
                }
            }

            // Slab
            nlohmann::json slab_boundary;
            if (story.contains("slab_boundary") && story["slab_boundary"].is_array()
                && !story["slab_boundary"].empty()) {
                slab_boundary = story["slab_boundary"];
            } else if (plan.contains("building_footprint")) {
                slab_boundary = plan["building_footprint"];
            }
            if (!slab_boundary.empty()) {
                double slab_thick = story.value("slab_thickness_m", 0.2);
                int sid = create_slab(storey_id, context_id,
                                      slab_boundary, elevation, slab_thick);
                elements.push_back(sid);
            }

            if (!elements.empty()) {
                add_rel_contained(storey_id, elements);
            }
        }
    }

    // Roof
    if (plan.contains("roof")) {
        nlohmann::json roof_boundary;
        if (plan.contains("building_footprint")) {
            roof_boundary = plan["building_footprint"];
        }
        if (!roof_boundary.empty() && !storey_ids.empty()) {
            double roof_z = 0.0;
            if (stories.is_array() && !stories.empty()) {
                auto& last = stories.back();
                roof_z = last.value("elevation_m", 0.0) + last.value("height_m", 3.0);
            }
            int roof_id = create_roof(storey_ids.back(), context_id,
                                       roof_boundary, roof_z, 0.15);
            // Roof contained in last storey
            add_rel_contained(storey_ids.back(), {roof_id});
        }
    }

    // Aggregation relationships
    if (!storey_ids.empty()) {
        add_rel_aggregates(building_id, storey_ids);
    }
    add_rel_aggregates(site_id, {building_id});
    add_rel_aggregates(project_id, {site_id});

    // Build output
    std::string filename = "model.ifc";
    return build_header(filename) + build_data();
}

// -------------------------------------------------------------------------
// IFC structure helpers
// -------------------------------------------------------------------------

int IFCGenerator::create_units() {
    int length = add_entity("IFCSIUNIT", "(*,$,.LENGTHUNIT.,$,.METRE.)");
    int area = add_entity("IFCSIUNIT", "(*,$,.AREAUNIT.,$,.SQUARE_METRE.)");
    int volume = add_entity("IFCSIUNIT", "(*,$,.VOLUMEUNIT.,$,.CUBIC_METRE.)");
    int angle = add_entity("IFCSIUNIT", "(*,$,.PLANEANGLEUNIT.,$,.RADIAN.)");
    std::ostringstream oss;
    oss << "(#" << length << ",#" << area << ",#" << volume << ",#" << angle << ")";
    return add_entity("IFCUNITASSIGNMENT", oss.str());
}

int IFCGenerator::create_geometric_context() {
    int origin = create_axis2_placement_3d(0, 0, 0);
    std::ostringstream oss;
    oss << "('Model','Model',3,1.E-05,#" << origin << ",$)";
    return add_entity("IFCGEOMETRICREPRESENTATIONCONTEXT", oss.str());
}

int IFCGenerator::create_project(const std::string& name) {
    int units = 0;
    // Find the unit assignment entity
    for (auto& e : entities_) {
        if (e.type == "IFCUNITASSIGNMENT") {
            units = e.id;
            break;
        }
    }
    int ctx = 0;
    for (auto& e : entities_) {
        if (e.type == "IFCGEOMETRICREPRESENTATIONCONTEXT") {
            ctx = e.id;
            break;
        }
    }
    std::ostringstream oss;
    oss << "('project-guid-001',$,'" << name
        << "',$,$,$,(#" << ctx << "),#" << units << ")";
    return add_entity("IFCPROJECT", oss.str());
}

int IFCGenerator::create_site(int project_id) {
    int placement = create_axis2_placement_3d(0, 0, 0);
    int local_placement = create_local_placement(0, placement);
    std::ostringstream oss;
    oss << "('site-guid-001',$,'Default Site',$,$,#"
        << local_placement << ",$,$,.ELEMENT.,$,$,$,$,$)";
    return add_entity("IFCSITE", oss.str());
}

int IFCGenerator::create_building(int site_id, const std::string& name) {
    int placement = create_axis2_placement_3d(0, 0, 0);
    int local_placement = create_local_placement(0, placement);
    std::ostringstream oss;
    oss << "('bldg-guid-001',$,'" << name << "',$,$,#"
        << local_placement << ",$,$,.ELEMENT.,$,$,$)";
    return add_entity("IFCBUILDING", oss.str());
}

int IFCGenerator::create_storey(int building_id, const std::string& name,
                                 double elevation) {
    int placement = create_axis2_placement_3d(0, 0, elevation);
    int local_placement = create_local_placement(0, placement);
    std::ostringstream oss;
    oss << "('storey-guid-" << name << "',$,'" << name << "',$,$,#"
        << local_placement << ",$,$,.ELEMENT.," << std::fixed
        << std::setprecision(2) << elevation << ")";
    return add_entity("IFCBUILDINGSTOREY", oss.str());
}

// -------------------------------------------------------------------------
// Geometry creation
// -------------------------------------------------------------------------

int IFCGenerator::create_axis2_placement_3d(double x, double y, double z,
                                             double dx, double dy, double dz,
                                             double rx, double ry, double rz) {
    std::ostringstream oss;
    oss << std::fixed << std::setprecision(4);

    // Point
    oss.str("");
    oss << "(" << x << "," << y << "," << z << ")";
    int point = add_entity("IFCCARTESIANPOINT", oss.str());

    // Z direction
    oss.str("");
    oss << "(" << dx << "," << dy << "," << dz << ")";
    int dir_z = add_entity("IFCDIRECTION", oss.str());

    // X direction
    oss.str("");
    oss << "(" << rx << "," << ry << "," << rz << ")";
    int dir_x = add_entity("IFCDIRECTION", oss.str());

    oss.str("");
    oss << "(#" << point << ",#" << dir_z << ",#" << dir_x << ")";
    return add_entity("IFCAXIS2PLACEMENT3D", oss.str());
}

int IFCGenerator::create_local_placement(int parent_placement, int axis_placement) {
    std::ostringstream oss;
    if (parent_placement > 0) {
        oss << "(#" << parent_placement << ",#" << axis_placement << ")";
    } else {
        oss << "($,#" << axis_placement << ")";
    }
    return add_entity("IFCLOCALPLACEMENT", oss.str());
}

int IFCGenerator::create_wall_extruded_solid(double length, double height,
                                              double thickness) {
    // Create rectangular profile
    std::ostringstream oss;
    oss << std::fixed << std::setprecision(4);

    // Profile position (centered on wall axis)
    oss.str("");
    oss << "(" << 0.0 << "," << 0.0 << ")";
    int center = add_entity("IFCCARTESIANPOINT", oss.str());
    oss.str("");
    oss << "(#" << center << ")";
    int pos2d = add_entity("IFCAXIS2PLACEMENT2D", oss.str());

    oss.str("");
    oss << "(.AREA.,$,#" << pos2d << "," << length << "," << thickness << ")";
    int profile = add_entity("IFCRECTANGLEPROFILEDEF", oss.str());

    // Extrusion direction (up)
    oss.str("");
    oss << "(0.0000,0.0000,1.0000)";
    int dir = add_entity("IFCDIRECTION", oss.str());

    // Position for extrusion
    int axis = create_axis2_placement_3d(0, 0, 0);

    oss.str("");
    oss << "(#" << axis << ",#" << dir << "," << height << ",#" << profile << ")";
    return add_entity("IFCEXTRUDEDAREASOLID", oss.str());
}

int IFCGenerator::create_extruded_area_solid(const nlohmann::json& boundary,
                                              double depth) {
    std::ostringstream oss;
    oss << std::fixed << std::setprecision(4);

    // Build polyline from boundary points
    std::vector<int> point_ids;
    for (auto& pt : boundary) {
        double x = pt[0].get<double>();
        double y = pt[1].get<double>();
        oss.str("");
        oss << "(" << x << "," << y << ")";
        point_ids.push_back(add_entity("IFCCARTESIANPOINT", oss.str()));
    }
    // Close the loop
    if (!point_ids.empty()) {
        point_ids.push_back(point_ids[0]);
    }

    oss.str("");
    oss << "(";
    for (size_t i = 0; i < point_ids.size(); ++i) {
        if (i > 0) oss << ",";
        oss << "#" << point_ids[i];
    }
    oss << ")";
    int polyline = add_entity("IFCPOLYLINE", oss.str());

    oss.str("");
    oss << "(#" << polyline << ")";
    int profile = add_entity("IFCARBITRARYCLOSEDPROFILEDEF", oss.str());

    // Extrusion direction
    oss.str("");
    oss << "(0.0000,0.0000,1.0000)";
    int dir = add_entity("IFCDIRECTION", oss.str());

    int axis = create_axis2_placement_3d(0, 0, 0);

    oss.str("");
    oss << "(#" << axis << ",#" << dir << "," << depth << ",#" << profile << ")";
    return add_entity("IFCEXTRUDEDAREASOLID", oss.str());
}

int IFCGenerator::create_shape_representation(int context_id, int solid_id) {
    std::ostringstream oss;
    oss << "(#" << context_id << ",'Body','SweptSolid',(#" << solid_id << "))";
    return add_entity("IFCSHAPEREPRESENTATION", oss.str());
}

int IFCGenerator::create_product_definition_shape(int shape_rep_id) {
    std::ostringstream oss;
    oss << "($,$,(#" << shape_rep_id << "))";
    return add_entity("IFCPRODUCTDEFINITIONSHAPE", oss.str());
}

// -------------------------------------------------------------------------
// Element creation
// -------------------------------------------------------------------------

int IFCGenerator::create_wall(int storey_id, int context_id,
                               double sx, double sy, double ex, double ey,
                               double base_z, double height, double thickness,
                               const std::string& wall_type) {
    if (!is_valid_coord(sx) || !is_valid_coord(sy) ||
        !is_valid_coord(ex) || !is_valid_coord(ey) ||
        !is_valid_coord(base_z) || !is_valid_coord(height) ||
        !is_valid_coord(thickness)) {
        return -1;
    }
    double dx = ex - sx;
    double dy = ey - sy;
    double length = std::sqrt(dx * dx + dy * dy);
    double angle = std::atan2(dy, dx);

    // Mid-point placement
    double mx = (sx + ex) / 2.0;
    double my = (sy + ey) / 2.0;

    // Wall axis placement with rotation
    int axis = create_axis2_placement_3d(
        mx, my, base_z,
        0, 0, 1,           // Z axis (up)
        std::cos(angle), std::sin(angle), 0  // X axis (along wall)
    );
    int placement = create_local_placement(0, axis);

    // Geometry
    int solid = create_wall_extruded_solid(length, height, thickness);
    int shape_rep = create_shape_representation(context_id, solid);
    int prod_shape = create_product_definition_shape(shape_rep);

    // Material
    double r = 0.75, g = 0.75, b = 0.75;
    if (wall_type == "exterior") { r = 0.78; g = 0.76; b = 0.72; }
    else if (wall_type == "partition") { r = 0.90; g = 0.88; b = 0.85; }
    get_or_create_material(wall_type + "_wall", r, g, b);

    std::ostringstream oss;
    oss << "('wall-" << next_id_ + 1 << "',$,'Wall',$,$,#"
        << placement << ",#" << prod_shape << ",$,$)";
    return add_entity("IFCWALL", oss.str());
}

int IFCGenerator::create_slab(int storey_id, int context_id,
                               const nlohmann::json& boundary, double elevation,
                               double thickness) {
    int axis = create_axis2_placement_3d(0, 0, elevation);
    int placement = create_local_placement(0, axis);

    int solid = create_extruded_area_solid(boundary, thickness);
    int shape_rep = create_shape_representation(context_id, solid);
    int prod_shape = create_product_definition_shape(shape_rep);

    get_or_create_material("concrete_slab", 0.70, 0.70, 0.70);

    std::ostringstream oss;
    oss << "('slab-" << next_id_ + 1 << "',$,'Slab',$,$,#"
        << placement << ",#" << prod_shape << ",$,$)";
    return add_entity("IFCSLAB", oss.str());
}

int IFCGenerator::create_roof(int storey_id, int context_id,
                               const nlohmann::json& boundary, double base_z,
                               double thickness) {
    int axis = create_axis2_placement_3d(0, 0, base_z);
    int placement = create_local_placement(0, axis);

    int solid = create_extruded_area_solid(boundary, thickness);
    int shape_rep = create_shape_representation(context_id, solid);
    int prod_shape = create_product_definition_shape(shape_rep);

    get_or_create_material("roof_tile", 0.55, 0.27, 0.07);

    std::ostringstream oss;
    oss << "('roof-" << next_id_ + 1 << "',$,'Roof',$,$,#"
        << placement << ",#" << prod_shape << ",$,$)";
    return add_entity("IFCROOF", oss.str());
}

// -------------------------------------------------------------------------
// Material
// -------------------------------------------------------------------------

int IFCGenerator::get_or_create_material(const std::string& name,
                                          double r, double g, double b) {
    auto it = material_cache_.find(name);
    if (it != material_cache_.end()) return it->second;

    std::ostringstream oss;
    oss << "('" << name << "')";
    int mat_id = add_entity("IFCMATERIAL", oss.str());

    // Surface style
    oss.str("");
    oss << std::fixed << std::setprecision(3);
    oss << "(" << r << "," << g << "," << b << ")";
    int color = add_entity("IFCCOLOURRGB", oss.str());

    oss.str("");
    oss << "(#" << color << ",0.0,.NOTDEFINED.,$,$,$,$,$,.FLAT.)";
    int rendering = add_entity("IFCSURFACESTYLERENDERING", oss.str());

    oss.str("");
    oss << "(.BOTH.,(#" << rendering << "))";
    add_entity("IFCSURFACESTYLE", oss.str());

    material_cache_[name] = mat_id;
    return mat_id;
}

// -------------------------------------------------------------------------
// Relationships
// -------------------------------------------------------------------------

void IFCGenerator::add_rel_contained(int storey_id,
                                      const std::vector<int>& element_ids) {
    std::ostringstream oss;
    oss << "('rel-contains-" << next_id_ + 1 << "',$,$,$,#" << storey_id << ",(";
    for (size_t i = 0; i < element_ids.size(); ++i) {
        if (i > 0) oss << ",";
        oss << "#" << element_ids[i];
    }
    oss << "))";
    add_entity("IFCRELCONTAINEDINSPATIALSTRUCTURE", oss.str());
}

void IFCGenerator::add_rel_aggregates(int parent_id,
                                       const std::vector<int>& child_ids) {
    std::ostringstream oss;
    oss << "('rel-agg-" << next_id_ + 1 << "',$,$,$,#" << parent_id << ",(";
    for (size_t i = 0; i < child_ids.size(); ++i) {
        if (i > 0) oss << ",";
        oss << "#" << child_ids[i];
    }
    oss << "))";
    add_entity("IFCRELAGGREGATES", oss.str());
}

// -------------------------------------------------------------------------
// Output
// -------------------------------------------------------------------------

std::string IFCGenerator::build_header(const std::string& filename) {
    // Get current timestamp (thread-safe)
    time_t now = time(nullptr);
    struct tm t_buf;
    struct tm* t = gmtime_r(&now, &t_buf);
    char ts[64];
    std::strftime(ts, sizeof(ts), "%Y-%m-%dT%H:%M:%S", t);

    std::ostringstream oss;
    oss << "ISO-10303-21;\n"
        << "HEADER;\n"
        << "FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');\n"
        << "FILE_NAME('" << filename << "','" << ts
        << "',('PromptBIM'),('Reality Matrix Inc.'),"
        << "'libpromptbim " << pb_version() << "','libpromptbim','');\n"
        << "FILE_SCHEMA(('IFC4'));\n"
        << "ENDSEC;\n\n";
    return oss.str();
}

std::string IFCGenerator::build_data() {
    std::ostringstream oss;
    oss << "DATA;\n";
    for (auto& e : entities_) {
        oss << "#" << e.id << "=" << e.type << e.args << ";\n";
    }
    oss << "ENDSEC;\n"
        << "END-ISO-10303-21;\n";
    return oss.str();
}

} // namespace promptbim

// =========================================================================
// C ABI implementation — replaces future_stubs.cpp placeholders
// =========================================================================

#include "pb_plan_internal.h"

PBPlan* pb_plan_from_json(const char* json_str) {
    if (!json_str) return nullptr;
    try {
        // Validate JSON (parse to confirm it's valid)
        auto parsed = nlohmann::json::parse(json_str);
        (void)parsed;
        auto* plan = new PBPlan();
        plan->json_data = json_str;
        return plan;
    } catch (...) {
        return nullptr;
    }
}

void pb_plan_free(PBPlan* plan) {
    delete plan;
}

char* pb_plan_to_json(const PBPlan* plan) {
    if (!plan) return nullptr;
    char* result = static_cast<char*>(std::malloc(plan->json_data.size() + 1));
    if (result) {
        std::memcpy(result, plan->json_data.c_str(), plan->json_data.size() + 1);
    }
    return result;
}

int pb_generate_ifc(const PBPlan* plan, const char* output_path) {
    if (!plan || !output_path) return -1;
    promptbim::IFCGenerator gen;
    return gen.generate(plan->json_data, output_path);
}
