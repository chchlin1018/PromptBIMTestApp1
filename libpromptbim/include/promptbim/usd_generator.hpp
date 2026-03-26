/**
 * usd_generator.hpp — USD ASCII (.usda) and USDZ generator
 *
 * Generates OpenUSD files directly in C++ by writing the text-based
 * USDA format. No external dependency on the pxr:: C++ SDK.
 * Produces valid .usda files and .usdz archives.
 *
 * Phase 3: V2 Migration — Sprint P20
 */

#pragma once

#include <nlohmann/json.hpp>
#include <string>
#include <vector>
#include <map>

namespace promptbim {

struct Mesh {
    std::vector<std::array<double, 3>> points;
    std::vector<int> face_vertex_counts;
    std::vector<int> face_vertex_indices;
    std::vector<std::array<double, 3>> normals;
};

class USDGenerator {
public:
    USDGenerator();

    /**
     * Generate a USDA file from a BuildingPlan JSON.
     * @param plan_json BuildingPlan serialized as JSON string
     * @param output_path Path to write the .usda file
     * @return 0 on success, -1 on error
     */
    int generate(const std::string& plan_json, const std::string& output_path);

    /**
     * Generate USDA content as a string (for testing).
     * @param plan_json BuildingPlan serialized as JSON string
     * @return USDA content string, empty on error
     */
    std::string generate_string(const std::string& plan_json);

    /**
     * Package a .usda file into a .usdz archive.
     * USDZ is a zip archive (uncompressed) containing a .usda root file.
     * @param usd_path  Path to the .usda input file
     * @param output_path Path to write the .usdz file
     * @return 0 on success, -1 on error
     */
    static int package_usdz(const std::string& usd_path,
                             const std::string& output_path);

private:
    std::map<std::string, bool> material_cache_;
    std::string output_;
    int indent_;

    void reset();
    void write_line(const std::string& line);
    void begin_block(const std::string& header);
    void end_block();

    // USD structure
    void write_header();
    void write_building(const nlohmann::json& plan);
    void write_story(const nlohmann::json& story,
                     const nlohmann::json& footprint, int story_idx);
    void write_wall(const nlohmann::json& wall,
                    double base_z, double height, int idx);
    void write_slab(const nlohmann::json& boundary,
                    double elevation, double thickness, const std::string& name);
    void write_roof(const nlohmann::json& boundary,
                    double base_z, const std::string& roof_type);
    void write_mesh(const std::string& name, const Mesh& mesh);
    void write_material(const std::string& name,
                        double r, double g, double b,
                        double roughness = 0.7, double metallic = 0.0,
                        double opacity = 1.0);

    // Geometry generation
    static Mesh wall_mesh(double sx, double sy, double ex, double ey,
                          double height, double thickness, double base_z);
    static Mesh slab_mesh(const nlohmann::json& boundary,
                          double thickness, double base_z);
    static Mesh flat_roof_mesh(const nlohmann::json& boundary, double base_z);

    // Material mapping
    struct MaterialDef {
        double r, g, b;
        double roughness;
        double metallic;
        double opacity;
    };
    static MaterialDef wall_material(const std::string& wall_type);
    static MaterialDef slab_material();
    static MaterialDef roof_material(const std::string& roof_type);

    // Utilities
    static std::string safe_name(const std::string& name);
};

} // namespace promptbim
