/**
 * ifc_generator.hpp — IFC-SPF (STEP Physical File) generator
 *
 * Generates IFC4 files directly in C++ by writing the text-based
 * IFC-SPF format. No external dependency on IfcOpenShell C++ SDK
 * (which requires OpenCASCADE). Produces valid .ifc files that can
 * be opened by any IFC viewer.
 *
 * Phase 3: V2 Migration — Sprint P20
 */

#pragma once

#include <nlohmann/json.hpp>
#include <string>
#include <vector>
#include <map>
#include <cmath>

namespace promptbim {

struct IFCEntity {
    int id;
    std::string type;
    std::string args;
};

class IFCGenerator {
public:
    IFCGenerator();

    /**
     * Generate an IFC4 file from a BuildingPlan JSON.
     * @param plan_json BuildingPlan serialized as JSON string
     * @param output_path Path to write the .ifc file
     * @return 0 on success, -1 on error
     */
    int generate(const std::string& plan_json, const std::string& output_path);

    /**
     * Generate IFC content as a string (for testing).
     * @param plan_json BuildingPlan serialized as JSON string
     * @return IFC-SPF content string, empty on error
     */
    std::string generate_string(const std::string& plan_json);

private:
    int next_id_;
    std::vector<IFCEntity> entities_;
    std::map<std::string, int> material_cache_;

    int add_entity(const std::string& type, const std::string& args);

    // IFC structure creation
    int create_project(const std::string& name);
    int create_site(int project_id);
    int create_building(int site_id, const std::string& name);
    int create_storey(int building_id, const std::string& name, double elevation);
    int create_geometric_context();
    int create_units();

    // Element creation
    int create_wall(int storey_id, int context_id,
                    double sx, double sy, double ex, double ey,
                    double base_z, double height, double thickness,
                    const std::string& wall_type);
    int create_slab(int storey_id, int context_id,
                    const nlohmann::json& boundary, double elevation,
                    double thickness);
    int create_roof(int storey_id, int context_id,
                    const nlohmann::json& boundary, double base_z,
                    double thickness);

    // Geometry helpers
    int create_axis2_placement_3d(double x, double y, double z,
                                   double dx = 0, double dy = 0, double dz = 1,
                                   double rx = 1, double ry = 0, double rz = 0);
    int create_local_placement(int parent_placement, int axis_placement);
    int create_extruded_area_solid(const nlohmann::json& boundary, double depth);
    int create_wall_extruded_solid(double length, double height, double thickness);
    int create_shape_representation(int context_id, int solid_id);
    int create_product_definition_shape(int shape_rep_id);

    // Material
    int get_or_create_material(const std::string& name,
                               double r, double g, double b);

    // Relationships
    void add_rel_contained(int storey_id, const std::vector<int>& element_ids);
    void add_rel_aggregates(int parent_id, const std::vector<int>& child_ids);

    // Output
    std::string build_header(const std::string& filename);
    std::string build_data();

    // Reset state
    void reset();
};

} // namespace promptbim
