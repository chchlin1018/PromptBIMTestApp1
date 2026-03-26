/**
 * usd_generator.cpp — USD ASCII (.usda) and USDZ generator
 *
 * Writes valid USDA files directly, matching the output structure of the
 * Python USDGenerator (which uses pxr.Usd/UsdGeom/UsdShade).
 * Also implements USDZ packaging (uncompressed zip archive).
 *
 * Phase 3: V2 Migration — Sprint P20
 */

#include "promptbim/usd_generator.hpp"
#include "promptbim/promptbim.h"
#include "pb_plan_internal.h"

#include <algorithm>
#include <cmath>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <cstdint>
#include <ctime>

namespace promptbim {

// -------------------------------------------------------------------------
// Construction / Reset
// -------------------------------------------------------------------------

USDGenerator::USDGenerator() : indent_(0) {}

void USDGenerator::reset() {
    output_.clear();
    material_cache_.clear();
    indent_ = 0;
}

// -------------------------------------------------------------------------
// Output helpers
// -------------------------------------------------------------------------

void USDGenerator::write_line(const std::string& line) {
    for (int i = 0; i < indent_; ++i) output_ += "    ";
    output_ += line + "\n";
}

void USDGenerator::begin_block(const std::string& header) {
    write_line(header);
    write_line("{");
    indent_++;
}

void USDGenerator::end_block() {
    indent_--;
    write_line("}");
    write_line("");
}

// -------------------------------------------------------------------------
// Public API
// -------------------------------------------------------------------------

int USDGenerator::generate(const std::string& plan_json,
                            const std::string& output_path) {
    std::string content = generate_string(plan_json);
    if (content.empty()) return -1;

    std::ofstream ofs(output_path);
    if (!ofs.is_open()) return -1;
    ofs << content;
    ofs.close();
    return 0;
}

std::string USDGenerator::generate_string(const std::string& plan_json) {
    reset();

    nlohmann::json plan;
    try {
        plan = nlohmann::json::parse(plan_json);
    } catch (...) {
        return "";
    }

    write_header();
    write_building(plan);

    return output_;
}

// -------------------------------------------------------------------------
// USD structure
// -------------------------------------------------------------------------

void USDGenerator::write_header() {
    write_line("#usda 1.0");
    begin_block("(");
    indent_--;
    write_line("    defaultPrim = \"Building\"");
    write_line("    metersPerUnit = 1.0");
    write_line("    upAxis = \"Z\"");
    write_line(")");
    write_line("");
}

void USDGenerator::write_building(const nlohmann::json& plan) {
    std::string name = plan.value("name", "Building");
    begin_block("def Xform \"Building\" (");
    indent_--;
    write_line("    kind = \"assembly\"");
    write_line(")");
    indent_++;

    // Process stories
    if (plan.contains("stories") && plan["stories"].is_array()) {
        int idx = 0;
        for (auto& story : plan["stories"]) {
            nlohmann::json footprint;
            if (plan.contains("building_footprint")) {
                footprint = plan["building_footprint"];
            }
            write_story(story, footprint, idx++);
        }
    }

    // Roof
    if (plan.contains("roof") && plan.contains("building_footprint")) {
        double roof_z = 0.0;
        if (plan.contains("stories") && plan["stories"].is_array()) {
            auto& stories = plan["stories"];
            if (!stories.empty()) {
                auto& last = stories.back();
                roof_z = last.value("elevation_m", 0.0) + last.value("height_m", 3.0);
            }
        }
        std::string roof_type = plan["roof"].value("roof_type", "flat");
        write_roof(plan["building_footprint"], roof_z, roof_type);
    }

    // Materials scope
    if (!material_cache_.empty()) {
        begin_block("def Scope \"Materials\"");
        // Materials are already written inline
        end_block();
    }

    end_block();
}

void USDGenerator::write_story(const nlohmann::json& story,
                                const nlohmann::json& footprint, int story_idx) {
    std::string name = safe_name(story.value("name", "Story_" + std::to_string(story_idx)));
    double elevation = story.value("elevation_m", 0.0);
    double height = story.value("height_m", 3.0);

    begin_block("def Xform \"" + name + "\"");

    // Walls
    if (story.contains("walls") && story["walls"].is_array()) {
        int widx = 0;
        for (auto& wall : story["walls"]) {
            write_wall(wall, elevation, height, widx++);
        }
    }

    // Slab
    nlohmann::json slab_boundary;
    if (story.contains("slab_boundary") && story["slab_boundary"].is_array()
        && !story["slab_boundary"].empty()) {
        slab_boundary = story["slab_boundary"];
    } else if (!footprint.empty()) {
        slab_boundary = footprint;
    }
    if (!slab_boundary.empty()) {
        double slab_thick = story.value("slab_thickness_m", 0.2);
        write_slab(slab_boundary, elevation, slab_thick, "Slab");
    }

    end_block();
}

void USDGenerator::write_wall(const nlohmann::json& wall,
                               double base_z, double height, int idx) {
    double sx = wall["start"][0].get<double>();
    double sy = wall["start"][1].get<double>();
    double ex = wall["end"][0].get<double>();
    double ey = wall["end"][1].get<double>();
    double thickness = wall.value("thickness_m", 0.2);
    std::string wall_type = wall.value("wall_type", "exterior");

    Mesh mesh = wall_mesh(sx, sy, ex, ey, height, thickness, base_z);
    write_mesh("Wall_" + std::to_string(idx), mesh);

    // Material binding
    auto mat = wall_material(wall_type);
    std::string mat_name = wall_type + "_wall";
    if (material_cache_.find(mat_name) == material_cache_.end()) {
        write_material(mat_name, mat.r, mat.g, mat.b, mat.roughness, mat.metallic, mat.opacity);
        material_cache_[mat_name] = true;
    }
}

void USDGenerator::write_slab(const nlohmann::json& boundary,
                               double elevation, double thickness,
                               const std::string& name) {
    Mesh mesh = slab_mesh(boundary, thickness, elevation);
    write_mesh(name, mesh);

    auto mat = slab_material();
    if (material_cache_.find("concrete_slab") == material_cache_.end()) {
        write_material("concrete_slab", mat.r, mat.g, mat.b, mat.roughness, mat.metallic, mat.opacity);
        material_cache_["concrete_slab"] = true;
    }
}

void USDGenerator::write_roof(const nlohmann::json& boundary,
                               double base_z, const std::string& roof_type) {
    Mesh mesh = flat_roof_mesh(boundary, base_z);
    write_mesh("Roof", mesh);

    auto mat = roof_material(roof_type);
    std::string mat_name = roof_type + "_roof";
    if (material_cache_.find(mat_name) == material_cache_.end()) {
        write_material(mat_name, mat.r, mat.g, mat.b, mat.roughness, mat.metallic, mat.opacity);
        material_cache_[mat_name] = true;
    }
}

// -------------------------------------------------------------------------
// Mesh writing
// -------------------------------------------------------------------------

void USDGenerator::write_mesh(const std::string& name, const Mesh& mesh) {
    begin_block("def Mesh \"" + safe_name(name) + "\"");

    // Points
    {
        std::ostringstream oss;
        oss << std::fixed << std::setprecision(4);
        oss << "point3f[] points = [";
        for (size_t i = 0; i < mesh.points.size(); ++i) {
            if (i > 0) oss << ", ";
            oss << "(" << mesh.points[i][0] << ", "
                << mesh.points[i][1] << ", "
                << mesh.points[i][2] << ")";
        }
        oss << "]";
        write_line(oss.str());
    }

    // Face vertex counts
    {
        std::ostringstream oss;
        oss << "int[] faceVertexCounts = [";
        for (size_t i = 0; i < mesh.face_vertex_counts.size(); ++i) {
            if (i > 0) oss << ", ";
            oss << mesh.face_vertex_counts[i];
        }
        oss << "]";
        write_line(oss.str());
    }

    // Face vertex indices
    {
        std::ostringstream oss;
        oss << "int[] faceVertexIndices = [";
        for (size_t i = 0; i < mesh.face_vertex_indices.size(); ++i) {
            if (i > 0) oss << ", ";
            oss << mesh.face_vertex_indices[i];
        }
        oss << "]";
        write_line(oss.str());
    }

    // Normals
    if (!mesh.normals.empty()) {
        std::ostringstream oss;
        oss << std::fixed << std::setprecision(4);
        oss << "normal3f[] normals = [";
        for (size_t i = 0; i < mesh.normals.size(); ++i) {
            if (i > 0) oss << ", ";
            oss << "(" << mesh.normals[i][0] << ", "
                << mesh.normals[i][1] << ", "
                << mesh.normals[i][2] << ")";
        }
        oss << "] (interpolation = \"faceVarying\")";
        write_line(oss.str());
    }

    end_block();
}

void USDGenerator::write_material(const std::string& name,
                                   double r, double g, double b,
                                   double roughness, double metallic,
                                   double opacity) {
    std::string sname = safe_name(name);
    begin_block("def Material \"" + sname + "\"");

    std::ostringstream oss;
    oss << std::fixed << std::setprecision(3);

    write_line("token outputs:surface.connect = </Building/Materials/"
               + sname + "/PBRShader.outputs:surface>");

    begin_block("def Shader \"PBRShader\"");
    write_line("uniform token info:id = \"UsdPreviewSurface\"");
    oss.str("");
    oss << "color3f inputs:diffuseColor = (" << r << ", " << g << ", " << b << ")";
    write_line(oss.str());
    oss.str("");
    oss << "float inputs:roughness = " << roughness;
    write_line(oss.str());
    oss.str("");
    oss << "float inputs:metallic = " << metallic;
    write_line(oss.str());
    if (opacity < 1.0) {
        oss.str("");
        oss << "float inputs:opacity = " << opacity;
        write_line(oss.str());
    }
    write_line("token outputs:surface");
    end_block();

    end_block();
}

// -------------------------------------------------------------------------
// Geometry generation
// -------------------------------------------------------------------------

Mesh USDGenerator::wall_mesh(double sx, double sy, double ex, double ey,
                              double height, double thickness, double base_z) {
    double dx = ex - sx;
    double dy = ey - sy;
    double length = std::sqrt(dx * dx + dy * dy);
    if (length < 1e-9) return {};

    // Perpendicular normal
    double nx = -dy / length;
    double ny = dx / length;
    double half_t = thickness / 2.0;

    // 8 vertices: 4 bottom, 4 top
    Mesh mesh;
    mesh.points = {
        {sx + nx * half_t, sy + ny * half_t, base_z},
        {ex + nx * half_t, ey + ny * half_t, base_z},
        {ex - nx * half_t, ey - ny * half_t, base_z},
        {sx - nx * half_t, sy - ny * half_t, base_z},
        {sx + nx * half_t, sy + ny * half_t, base_z + height},
        {ex + nx * half_t, ey + ny * half_t, base_z + height},
        {ex - nx * half_t, ey - ny * half_t, base_z + height},
        {sx - nx * half_t, sy - ny * half_t, base_z + height},
    };

    // 6 quads (as triangles: 12 faces)
    mesh.face_vertex_counts = {3,3, 3,3, 3,3, 3,3, 3,3, 3,3};
    mesh.face_vertex_indices = {
        // Bottom (facing down)
        0, 2, 1,  0, 3, 2,
        // Top (facing up)
        4, 5, 6,  4, 6, 7,
        // Front
        0, 1, 5,  0, 5, 4,
        // Back
        2, 3, 7,  2, 7, 6,
        // Left
        3, 0, 4,  3, 4, 7,
        // Right
        1, 2, 6,  1, 6, 5,
    };

    return mesh;
}

Mesh USDGenerator::slab_mesh(const nlohmann::json& boundary,
                              double thickness, double base_z) {
    if (!boundary.is_array() || boundary.size() < 3) return {};

    size_t n = boundary.size();
    Mesh mesh;

    // Bottom + top vertices
    for (size_t i = 0; i < n; ++i) {
        double x = boundary[i][0].get<double>();
        double y = boundary[i][1].get<double>();
        mesh.points.push_back({x, y, base_z});
    }
    for (size_t i = 0; i < n; ++i) {
        double x = boundary[i][0].get<double>();
        double y = boundary[i][1].get<double>();
        mesh.points.push_back({x, y, base_z + thickness});
    }

    // Simple fan triangulation for bottom (reversed winding)
    for (size_t i = 1; i + 1 < n; ++i) {
        mesh.face_vertex_counts.push_back(3);
        mesh.face_vertex_indices.push_back(0);
        mesh.face_vertex_indices.push_back(static_cast<int>(i + 1));
        mesh.face_vertex_indices.push_back(static_cast<int>(i));
    }

    // Top (normal winding)
    for (size_t i = 1; i + 1 < n; ++i) {
        mesh.face_vertex_counts.push_back(3);
        mesh.face_vertex_indices.push_back(static_cast<int>(n));
        mesh.face_vertex_indices.push_back(static_cast<int>(n + i));
        mesh.face_vertex_indices.push_back(static_cast<int>(n + i + 1));
    }

    // Side faces (quad strips as 2 triangles each)
    for (size_t i = 0; i < n; ++i) {
        size_t j = (i + 1) % n;
        int bi = static_cast<int>(i);
        int bj = static_cast<int>(j);
        int ti = static_cast<int>(n + i);
        int tj = static_cast<int>(n + j);

        mesh.face_vertex_counts.push_back(3);
        mesh.face_vertex_indices.push_back(bi);
        mesh.face_vertex_indices.push_back(bj);
        mesh.face_vertex_indices.push_back(tj);

        mesh.face_vertex_counts.push_back(3);
        mesh.face_vertex_indices.push_back(bi);
        mesh.face_vertex_indices.push_back(tj);
        mesh.face_vertex_indices.push_back(ti);
    }

    return mesh;
}

Mesh USDGenerator::flat_roof_mesh(const nlohmann::json& boundary, double base_z) {
    return slab_mesh(boundary, 0.15, base_z);
}

// -------------------------------------------------------------------------
// Material mapping
// -------------------------------------------------------------------------

USDGenerator::MaterialDef USDGenerator::wall_material(const std::string& wall_type) {
    if (wall_type == "exterior")  return {0.78, 0.76, 0.72, 0.8, 0.0, 1.0};
    if (wall_type == "partition") return {0.90, 0.88, 0.85, 0.9, 0.0, 1.0};
    return {0.85, 0.83, 0.80, 0.8, 0.0, 1.0}; // interior default
}

USDGenerator::MaterialDef USDGenerator::slab_material() {
    return {0.70, 0.70, 0.70, 0.7, 0.0, 1.0};
}

USDGenerator::MaterialDef USDGenerator::roof_material(const std::string& roof_type) {
    if (roof_type == "flat") return {0.70, 0.70, 0.70, 0.7, 0.0, 1.0};
    return {0.55, 0.27, 0.07, 0.6, 0.0, 1.0}; // tile
}

// -------------------------------------------------------------------------
// USDZ packaging (uncompressed zip)
// -------------------------------------------------------------------------

// Minimal zip implementation for USDZ (must be uncompressed per spec)
namespace {

struct ZipLocalFileHeader {
    uint32_t signature = 0x04034b50;
    uint16_t version_needed = 20;
    uint16_t flags = 0;
    uint16_t compression = 0; // store (uncompressed)
    uint16_t mod_time = 0;
    uint16_t mod_date = 0;
    uint32_t crc32 = 0;
    uint32_t compressed_size = 0;
    uint32_t uncompressed_size = 0;
    uint16_t filename_length = 0;
    uint16_t extra_length = 0;
};

struct ZipCentralDirEntry {
    uint32_t signature = 0x02014b50;
    uint16_t version_made = 20;
    uint16_t version_needed = 20;
    uint16_t flags = 0;
    uint16_t compression = 0;
    uint16_t mod_time = 0;
    uint16_t mod_date = 0;
    uint32_t crc32 = 0;
    uint32_t compressed_size = 0;
    uint32_t uncompressed_size = 0;
    uint16_t filename_length = 0;
    uint16_t extra_length = 0;
    uint16_t comment_length = 0;
    uint16_t disk_start = 0;
    uint16_t internal_attr = 0;
    uint32_t external_attr = 0;
    uint32_t local_header_offset = 0;
};

struct ZipEndOfCentralDir {
    uint32_t signature = 0x06054b50;
    uint16_t disk_number = 0;
    uint16_t disk_cd_start = 0;
    uint16_t entries_on_disk = 0;
    uint16_t total_entries = 0;
    uint32_t cd_size = 0;
    uint32_t cd_offset = 0;
    uint16_t comment_length = 0;
};

uint32_t crc32_compute(const char* data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= static_cast<uint8_t>(data[i]);
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

template<typename T>
void write_le(std::ofstream& ofs, T val) {
    ofs.write(reinterpret_cast<const char*>(&val), sizeof(T));
}

} // anonymous namespace

int USDGenerator::package_usdz(const std::string& usd_path,
                                const std::string& output_path) {
    // Read input USDA file
    std::ifstream ifs(usd_path, std::ios::binary);
    if (!ifs.is_open()) return -1;
    std::string content((std::istreambuf_iterator<char>(ifs)),
                         std::istreambuf_iterator<char>());
    ifs.close();

    if (content.empty()) return -1;

    // Extract just the filename from the path
    std::string filename = "model.usda";
    auto pos = usd_path.rfind('/');
    if (pos != std::string::npos) {
        filename = usd_path.substr(pos + 1);
    }

    uint32_t crc = crc32_compute(content.data(), content.size());
    uint32_t file_size = static_cast<uint32_t>(content.size());
    uint16_t fname_len = static_cast<uint16_t>(filename.size());

    // USDZ requires 64-byte alignment for data
    // Local header size: 30 + filename_length
    uint32_t header_size = 30 + fname_len;
    // Padding to align data to 64 bytes
    uint16_t padding = (64 - (header_size % 64)) % 64;

    std::ofstream ofs(output_path, std::ios::binary);
    if (!ofs.is_open()) return -1;

    // Local file header
    write_le<uint32_t>(ofs, 0x04034b50);
    write_le<uint16_t>(ofs, 20);
    write_le<uint16_t>(ofs, 0);
    write_le<uint16_t>(ofs, 0); // no compression
    write_le<uint16_t>(ofs, 0);
    write_le<uint16_t>(ofs, 0);
    write_le<uint32_t>(ofs, crc);
    write_le<uint32_t>(ofs, file_size);
    write_le<uint32_t>(ofs, file_size);
    write_le<uint16_t>(ofs, fname_len);
    write_le<uint16_t>(ofs, padding);
    ofs.write(filename.c_str(), fname_len);
    // Write padding zeros
    for (uint16_t i = 0; i < padding; ++i) ofs.put(0);
    // File data
    ofs.write(content.data(), content.size());

    uint32_t local_header_total = header_size + padding + file_size;

    // Central directory
    uint32_t cd_offset = local_header_total;
    write_le<uint32_t>(ofs, 0x02014b50);
    write_le<uint16_t>(ofs, 20);
    write_le<uint16_t>(ofs, 20);
    write_le<uint16_t>(ofs, 0);
    write_le<uint16_t>(ofs, 0);
    write_le<uint16_t>(ofs, 0);
    write_le<uint16_t>(ofs, 0);
    write_le<uint32_t>(ofs, crc);
    write_le<uint32_t>(ofs, file_size);
    write_le<uint32_t>(ofs, file_size);
    write_le<uint16_t>(ofs, fname_len);
    write_le<uint16_t>(ofs, 0); // extra
    write_le<uint16_t>(ofs, 0); // comment
    write_le<uint16_t>(ofs, 0); // disk
    write_le<uint16_t>(ofs, 0); // internal attr
    write_le<uint32_t>(ofs, 0); // external attr
    write_le<uint32_t>(ofs, 0); // local header offset
    ofs.write(filename.c_str(), fname_len);

    uint32_t cd_size = 46 + fname_len;

    // End of central directory
    write_le<uint32_t>(ofs, 0x06054b50);
    write_le<uint16_t>(ofs, 0);
    write_le<uint16_t>(ofs, 0);
    write_le<uint16_t>(ofs, 1);
    write_le<uint16_t>(ofs, 1);
    write_le<uint32_t>(ofs, cd_size);
    write_le<uint32_t>(ofs, cd_offset);
    write_le<uint16_t>(ofs, 0);

    ofs.close();
    return 0;
}

// -------------------------------------------------------------------------
// Utilities
// -------------------------------------------------------------------------

std::string USDGenerator::safe_name(const std::string& name) {
    std::string result;
    result.reserve(name.size());
    for (char c : name) {
        if (std::isalnum(static_cast<unsigned char>(c)) || c == '_') {
            result += c;
        } else {
            result += '_';
        }
    }
    if (!result.empty() && std::isdigit(static_cast<unsigned char>(result[0]))) {
        result = "F" + result;
    }
    if (result.empty()) result = "Unnamed";
    return result;
}

} // namespace promptbim

// =========================================================================
// C ABI — USD + USDZ generation
// =========================================================================

int pb_generate_usd(const PBPlan* plan, const char* output_path) {
    if (!plan || !output_path) return -1;
    promptbim::USDGenerator gen;
    return gen.generate(plan->json_data, output_path);
}

int pb_generate_usdz(const char* usd_path, const char* output_path) {
    if (!usd_path || !output_path) return -1;
    return promptbim::USDGenerator::package_usdz(usd_path, output_path);
}
