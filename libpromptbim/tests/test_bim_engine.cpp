/**
 * test_bim_engine.cpp — GoogleTest for USD Generator + USDZ + BIM Engine (Phase 3)
 *
 * Validates USDA output structure, USDZ packaging, and C ABI for BIM.
 * Sprint P20 — Task 7
 */

#include <gtest/gtest.h>
#include "promptbim/usd_generator.hpp"
#include "promptbim/ifc_generator.hpp"
#include "promptbim/promptbim.h"

#include <fstream>
#include <filesystem>
#include <string>
#include <cstdint>

namespace fs = std::filesystem;

// Same test plan used across all BIM tests for consistency
static const char* TEST_PLAN = R"({
    "name": "Test Office",
    "schema_version": "2.4.0",
    "building_footprint": [[0,0],[12,0],[12,10],[0,10]],
    "building_bcr": 0.55,
    "building_far": 1.65,
    "stories": [
        {
            "name": "Ground_Floor",
            "elevation_m": 0.0,
            "height_m": 4.0,
            "slab_thickness_m": 0.25,
            "walls": [
                {"start": [0,0], "end": [12,0], "thickness_m": 0.25, "wall_type": "exterior"},
                {"start": [12,0], "end": [12,10], "thickness_m": 0.25, "wall_type": "exterior"},
                {"start": [12,10], "end": [0,10], "thickness_m": 0.25, "wall_type": "exterior"},
                {"start": [0,10], "end": [0,0], "thickness_m": 0.25, "wall_type": "exterior"},
                {"start": [6,0], "end": [6,10], "thickness_m": 0.15, "wall_type": "partition"}
            ],
            "slab_boundary": [[0,0],[12,0],[12,10],[0,10]],
            "spaces": []
        },
        {
            "name": "Second_Floor",
            "elevation_m": 4.0,
            "height_m": 3.5,
            "slab_thickness_m": 0.2,
            "walls": [
                {"start": [0,0], "end": [12,0], "thickness_m": 0.25, "wall_type": "exterior"},
                {"start": [12,0], "end": [12,10], "thickness_m": 0.25, "wall_type": "exterior"},
                {"start": [12,10], "end": [0,10], "thickness_m": 0.25, "wall_type": "exterior"},
                {"start": [0,10], "end": [0,0], "thickness_m": 0.25, "wall_type": "exterior"}
            ],
            "slab_boundary": [[0,0],[12,0],[12,10],[0,10]],
            "spaces": []
        },
        {
            "name": "Third_Floor",
            "elevation_m": 7.5,
            "height_m": 3.0,
            "slab_thickness_m": 0.2,
            "walls": [
                {"start": [0,0], "end": [12,0], "thickness_m": 0.2, "wall_type": "exterior"},
                {"start": [12,0], "end": [12,10], "thickness_m": 0.2, "wall_type": "exterior"},
                {"start": [12,10], "end": [0,10], "thickness_m": 0.2, "wall_type": "exterior"},
                {"start": [0,10], "end": [0,0], "thickness_m": 0.2, "wall_type": "exterior"}
            ],
            "slab_boundary": [[0,0],[12,0],[12,10],[0,10]],
            "spaces": []
        }
    ],
    "roof": {"roof_type": "flat", "slope_deg": 0, "overhang_m": 0.3}
})";

// =========================================================================
// USD Generator Tests
// =========================================================================

class USDGeneratorTest : public ::testing::Test {
protected:
    promptbim::USDGenerator gen;
    std::string tmp_dir;

    void SetUp() override {
        tmp_dir = fs::temp_directory_path().string() + "/promptbim_test_usd";
        fs::create_directories(tmp_dir);
    }

    void TearDown() override {
        fs::remove_all(tmp_dir);
    }
};

TEST_F(USDGeneratorTest, GenerateStringProducesValidUSDA) {
    std::string usda = gen.generate_string(TEST_PLAN);
    ASSERT_FALSE(usda.empty());

    // Check USDA header
    EXPECT_NE(usda.find("#usda 1.0"), std::string::npos);
    EXPECT_NE(usda.find("metersPerUnit = 1.0"), std::string::npos);
    EXPECT_NE(usda.find("upAxis = \"Z\""), std::string::npos);
}

TEST_F(USDGeneratorTest, ContainsBuildingXform) {
    std::string usda = gen.generate_string(TEST_PLAN);
    EXPECT_NE(usda.find("def Xform \"Building\""), std::string::npos);
    EXPECT_NE(usda.find("kind = \"assembly\""), std::string::npos);
}

TEST_F(USDGeneratorTest, ContainsThreeStories) {
    std::string usda = gen.generate_string(TEST_PLAN);
    EXPECT_NE(usda.find("def Xform \"Ground_Floor\""), std::string::npos);
    EXPECT_NE(usda.find("def Xform \"Second_Floor\""), std::string::npos);
    EXPECT_NE(usda.find("def Xform \"Third_Floor\""), std::string::npos);
}

TEST_F(USDGeneratorTest, ContainsWallMeshes) {
    std::string usda = gen.generate_string(TEST_PLAN);
    EXPECT_NE(usda.find("def Mesh \"Wall_0\""), std::string::npos);
    EXPECT_NE(usda.find("point3f[] points"), std::string::npos);
    EXPECT_NE(usda.find("int[] faceVertexCounts"), std::string::npos);
    EXPECT_NE(usda.find("int[] faceVertexIndices"), std::string::npos);
}

TEST_F(USDGeneratorTest, ContainsSlabs) {
    std::string usda = gen.generate_string(TEST_PLAN);
    EXPECT_NE(usda.find("def Mesh \"Slab\""), std::string::npos);
}

TEST_F(USDGeneratorTest, ContainsRoof) {
    std::string usda = gen.generate_string(TEST_PLAN);
    EXPECT_NE(usda.find("def Mesh \"Roof\""), std::string::npos);
}

TEST_F(USDGeneratorTest, ContainsMaterials) {
    std::string usda = gen.generate_string(TEST_PLAN);
    EXPECT_NE(usda.find("def Material"), std::string::npos);
    EXPECT_NE(usda.find("UsdPreviewSurface"), std::string::npos);
    EXPECT_NE(usda.find("diffuseColor"), std::string::npos);
    EXPECT_NE(usda.find("roughness"), std::string::npos);
}

TEST_F(USDGeneratorTest, GenerateFileSuccess) {
    std::string path = tmp_dir + "/test_model.usda";
    int rc = gen.generate(TEST_PLAN, path);
    EXPECT_EQ(rc, 0);
    EXPECT_TRUE(fs::exists(path));
    EXPECT_GT(fs::file_size(path), 0u);
}

TEST_F(USDGeneratorTest, InvalidJsonReturnsEmpty) {
    std::string usda = gen.generate_string("{bad");
    EXPECT_TRUE(usda.empty());
}

TEST_F(USDGeneratorTest, InvalidJsonFileReturnsError) {
    int rc = gen.generate("{bad", tmp_dir + "/bad.usda");
    EXPECT_EQ(rc, -1);
}

// =========================================================================
// USDZ Packer Tests
// =========================================================================

TEST_F(USDGeneratorTest, PackageUSDZSuccess) {
    // First generate a USDA file
    std::string usda_path = tmp_dir + "/model.usda";
    gen.generate(TEST_PLAN, usda_path);

    // Package into USDZ
    std::string usdz_path = tmp_dir + "/model.usdz";
    int rc = promptbim::USDGenerator::package_usdz(usda_path, usdz_path);
    EXPECT_EQ(rc, 0);
    EXPECT_TRUE(fs::exists(usdz_path));
    EXPECT_GT(fs::file_size(usdz_path), 0u);
}

TEST_F(USDGeneratorTest, USDZContainsZipSignature) {
    std::string usda_path = tmp_dir + "/model.usda";
    gen.generate(TEST_PLAN, usda_path);

    std::string usdz_path = tmp_dir + "/model.usdz";
    promptbim::USDGenerator::package_usdz(usda_path, usdz_path);

    // Read first 4 bytes — should be PK zip signature
    std::ifstream ifs(usdz_path, std::ios::binary);
    uint32_t sig = 0;
    ifs.read(reinterpret_cast<char*>(&sig), 4);
    EXPECT_EQ(sig, 0x04034b50u); // PK\003\004
}

TEST_F(USDGeneratorTest, USDZContainsEndOfCentralDir) {
    std::string usda_path = tmp_dir + "/model.usda";
    gen.generate(TEST_PLAN, usda_path);

    std::string usdz_path = tmp_dir + "/model.usdz";
    promptbim::USDGenerator::package_usdz(usda_path, usdz_path);

    // Read file and check for end-of-central-dir signature
    std::ifstream ifs(usdz_path, std::ios::binary);
    std::string content((std::istreambuf_iterator<char>(ifs)),
                         std::istreambuf_iterator<char>());
    // Find 0x06054b50 signature
    bool found = false;
    for (size_t i = 0; i + 3 < content.size(); ++i) {
        uint32_t sig;
        std::memcpy(&sig, content.data() + i, 4);
        if (sig == 0x06054b50) { found = true; break; }
    }
    EXPECT_TRUE(found);
}

TEST_F(USDGeneratorTest, PackageUSDZMissingFile) {
    int rc = promptbim::USDGenerator::package_usdz("/nonexistent.usda", tmp_dir + "/x.usdz");
    EXPECT_EQ(rc, -1);
}

TEST_F(USDGeneratorTest, PackageUSDZNullArgs) {
    EXPECT_EQ(pb_generate_usdz(nullptr, "/tmp/x.usdz"), -1);
    EXPECT_EQ(pb_generate_usdz("/tmp/x.usda", nullptr), -1);
}

// =========================================================================
// C ABI BIM Tests
// =========================================================================

class BIMEngineCABITest : public ::testing::Test {
protected:
    std::string tmp_dir;

    void SetUp() override {
        tmp_dir = fs::temp_directory_path().string() + "/promptbim_test_bim_cabi";
        fs::create_directories(tmp_dir);
    }

    void TearDown() override {
        fs::remove_all(tmp_dir);
    }
};

TEST_F(BIMEngineCABITest, GenerateIFCViaCAPI) {
    PBPlan* plan = pb_plan_from_json(TEST_PLAN);
    ASSERT_NE(plan, nullptr);

    std::string path = tmp_dir + "/cabi.ifc";
    EXPECT_EQ(pb_generate_ifc(plan, path.c_str()), 0);
    EXPECT_TRUE(fs::exists(path));

    // Verify content
    std::ifstream ifs(path);
    std::string content((std::istreambuf_iterator<char>(ifs)),
                         std::istreambuf_iterator<char>());
    EXPECT_NE(content.find("IFCWALL"), std::string::npos);
    EXPECT_NE(content.find("IFCSLAB"), std::string::npos);

    pb_plan_free(plan);
}

TEST_F(BIMEngineCABITest, GenerateUSDViaCAPI) {
    PBPlan* plan = pb_plan_from_json(TEST_PLAN);
    ASSERT_NE(plan, nullptr);

    std::string path = tmp_dir + "/cabi.usda";
    EXPECT_EQ(pb_generate_usd(plan, path.c_str()), 0);
    EXPECT_TRUE(fs::exists(path));

    // Verify content
    std::ifstream ifs(path);
    std::string content((std::istreambuf_iterator<char>(ifs)),
                         std::istreambuf_iterator<char>());
    EXPECT_NE(content.find("#usda 1.0"), std::string::npos);
    EXPECT_NE(content.find("def Mesh"), std::string::npos);

    pb_plan_free(plan);
}

TEST_F(BIMEngineCABITest, GenerateUSDZViaCAPI) {
    PBPlan* plan = pb_plan_from_json(TEST_PLAN);
    ASSERT_NE(plan, nullptr);

    std::string usda_path = tmp_dir + "/cabi.usda";
    pb_generate_usd(plan, usda_path.c_str());

    std::string usdz_path = tmp_dir + "/cabi.usdz";
    EXPECT_EQ(pb_generate_usdz(usda_path.c_str(), usdz_path.c_str()), 0);
    EXPECT_TRUE(fs::exists(usdz_path));

    pb_plan_free(plan);
}

TEST_F(BIMEngineCABITest, PlanRoundTrip) {
    PBPlan* plan = pb_plan_from_json(TEST_PLAN);
    ASSERT_NE(plan, nullptr);

    char* json_out = pb_plan_to_json(plan);
    ASSERT_NE(json_out, nullptr);

    // Parse and check key fields survived the round trip
    auto parsed = nlohmann::json::parse(json_out);
    EXPECT_EQ(parsed["name"].get<std::string>(), "Test Office");
    EXPECT_EQ(parsed["stories"].size(), 3);

    pb_free_string(json_out);
    pb_plan_free(plan);
}

TEST_F(BIMEngineCABITest, IFCAndUSDProduceDifferentFormats) {
    PBPlan* plan = pb_plan_from_json(TEST_PLAN);
    ASSERT_NE(plan, nullptr);

    std::string ifc_path = tmp_dir + "/compare.ifc";
    std::string usd_path = tmp_dir + "/compare.usda";

    pb_generate_ifc(plan, ifc_path.c_str());
    pb_generate_usd(plan, usd_path.c_str());

    std::ifstream ifs_ifc(ifc_path);
    std::string ifc_content((std::istreambuf_iterator<char>(ifs_ifc)),
                             std::istreambuf_iterator<char>());

    std::ifstream ifs_usd(usd_path);
    std::string usd_content((std::istreambuf_iterator<char>(ifs_usd)),
                             std::istreambuf_iterator<char>());

    // IFC should have ISO-10303 markers, USD should have usda header
    EXPECT_NE(ifc_content.find("ISO-10303-21"), std::string::npos);
    EXPECT_EQ(ifc_content.find("#usda"), std::string::npos);

    EXPECT_NE(usd_content.find("#usda 1.0"), std::string::npos);
    EXPECT_EQ(usd_content.find("ISO-10303"), std::string::npos);

    pb_plan_free(plan);
}

TEST_F(BIMEngineCABITest, ThreeStoriesInBothFormats) {
    PBPlan* plan = pb_plan_from_json(TEST_PLAN);
    ASSERT_NE(plan, nullptr);

    // IFC: count IFCBUILDINGSTOREY
    promptbim::IFCGenerator ifc_gen;
    std::string ifc = ifc_gen.generate_string(TEST_PLAN);
    size_t storey_count = 0;
    size_t pos = 0;
    while ((pos = ifc.find("IFCBUILDINGSTOREY", pos)) != std::string::npos) {
        ++storey_count;
        pos += 17;
    }
    EXPECT_EQ(storey_count, 3);

    // USD: check for all three Xform storeys
    promptbim::USDGenerator usd_gen;
    std::string usda = usd_gen.generate_string(TEST_PLAN);
    EXPECT_NE(usda.find("Ground_Floor"), std::string::npos);
    EXPECT_NE(usda.find("Second_Floor"), std::string::npos);
    EXPECT_NE(usda.find("Third_Floor"), std::string::npos);

    pb_plan_free(plan);
}
