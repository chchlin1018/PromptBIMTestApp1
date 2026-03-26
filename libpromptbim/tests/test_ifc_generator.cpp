/**
 * test_ifc_generator.cpp — GoogleTest for IFC Generator (Phase 3)
 *
 * Validates IFC-SPF output structure, entity presence, and file I/O.
 * Sprint P20 — Task 3
 */

#include <gtest/gtest.h>
#include "promptbim/ifc_generator.hpp"
#include "promptbim/promptbim.h"

#include <fstream>
#include <filesystem>
#include <string>

namespace fs = std::filesystem;

// Minimal valid BuildingPlan JSON for testing
static const char* MINIMAL_PLAN = R"({
    "name": "Test Building",
    "schema_version": "2.4.0",
    "building_footprint": [[0,0],[10,0],[10,8],[0,8]],
    "building_bcr": 0.5,
    "building_far": 1.0,
    "stories": [
        {
            "name": "1F",
            "elevation_m": 0.0,
            "height_m": 3.5,
            "slab_thickness_m": 0.2,
            "walls": [
                {"start": [0,0], "end": [10,0], "thickness_m": 0.2, "wall_type": "exterior"},
                {"start": [10,0], "end": [10,8], "thickness_m": 0.2, "wall_type": "exterior"},
                {"start": [10,8], "end": [0,8], "thickness_m": 0.2, "wall_type": "exterior"},
                {"start": [0,8], "end": [0,0], "thickness_m": 0.2, "wall_type": "exterior"}
            ],
            "slab_boundary": [[0,0],[10,0],[10,8],[0,8]],
            "spaces": []
        },
        {
            "name": "2F",
            "elevation_m": 3.5,
            "height_m": 3.0,
            "slab_thickness_m": 0.2,
            "walls": [
                {"start": [0,0], "end": [10,0], "thickness_m": 0.2, "wall_type": "exterior"},
                {"start": [10,0], "end": [10,8], "thickness_m": 0.2, "wall_type": "exterior"},
                {"start": [10,8], "end": [0,8], "thickness_m": 0.2, "wall_type": "exterior"},
                {"start": [0,8], "end": [0,0], "thickness_m": 0.2, "wall_type": "exterior"}
            ],
            "slab_boundary": [[0,0],[10,0],[10,8],[0,8]],
            "spaces": []
        }
    ],
    "roof": {"roof_type": "flat", "slope_deg": 0, "overhang_m": 0}
})";

class IFCGeneratorTest : public ::testing::Test {
protected:
    promptbim::IFCGenerator gen;
    std::string tmp_dir;

    void SetUp() override {
        tmp_dir = fs::temp_directory_path().string() + "/promptbim_test_ifc";
        fs::create_directories(tmp_dir);
    }

    void TearDown() override {
        fs::remove_all(tmp_dir);
    }
};

TEST_F(IFCGeneratorTest, GenerateStringProducesValidIFC) {
    std::string ifc = gen.generate_string(MINIMAL_PLAN);
    ASSERT_FALSE(ifc.empty());

    // Check IFC-SPF header markers
    EXPECT_NE(ifc.find("ISO-10303-21;"), std::string::npos);
    EXPECT_NE(ifc.find("FILE_SCHEMA(('IFC4'));"), std::string::npos);
    EXPECT_NE(ifc.find("ENDSEC;"), std::string::npos);
    EXPECT_NE(ifc.find("END-ISO-10303-21;"), std::string::npos);
}

TEST_F(IFCGeneratorTest, ContainsProjectAndBuilding) {
    std::string ifc = gen.generate_string(MINIMAL_PLAN);
    EXPECT_NE(ifc.find("IFCPROJECT"), std::string::npos);
    EXPECT_NE(ifc.find("IFCSITE"), std::string::npos);
    EXPECT_NE(ifc.find("IFCBUILDING"), std::string::npos);
    EXPECT_NE(ifc.find("IFCBUILDINGSTOREY"), std::string::npos);
}

TEST_F(IFCGeneratorTest, ContainsWallsAndSlabs) {
    std::string ifc = gen.generate_string(MINIMAL_PLAN);
    EXPECT_NE(ifc.find("IFCWALL"), std::string::npos);
    EXPECT_NE(ifc.find("IFCSLAB"), std::string::npos);
}

TEST_F(IFCGeneratorTest, ContainsRoof) {
    std::string ifc = gen.generate_string(MINIMAL_PLAN);
    EXPECT_NE(ifc.find("IFCROOF"), std::string::npos);
}

TEST_F(IFCGeneratorTest, ContainsGeometryEntities) {
    std::string ifc = gen.generate_string(MINIMAL_PLAN);
    EXPECT_NE(ifc.find("IFCEXTRUDEDAREASOLID"), std::string::npos);
    EXPECT_NE(ifc.find("IFCSHAPEREPRESENTATION"), std::string::npos);
    EXPECT_NE(ifc.find("IFCLOCALPLACEMENT"), std::string::npos);
}

TEST_F(IFCGeneratorTest, ContainsMaterials) {
    std::string ifc = gen.generate_string(MINIMAL_PLAN);
    EXPECT_NE(ifc.find("IFCMATERIAL"), std::string::npos);
    EXPECT_NE(ifc.find("IFCCOLOURRGB"), std::string::npos);
}

TEST_F(IFCGeneratorTest, ContainsRelationships) {
    std::string ifc = gen.generate_string(MINIMAL_PLAN);
    EXPECT_NE(ifc.find("IFCRELAGGREGATES"), std::string::npos);
    EXPECT_NE(ifc.find("IFCRELCONTAINEDINSPATIALSTRUCTURE"), std::string::npos);
}

TEST_F(IFCGeneratorTest, ContainsTwoStoreys) {
    std::string ifc = gen.generate_string(MINIMAL_PLAN);
    // Count IFCBUILDINGSTOREY occurrences
    size_t count = 0;
    size_t pos = 0;
    while ((pos = ifc.find("IFCBUILDINGSTOREY", pos)) != std::string::npos) {
        ++count;
        pos += 17;
    }
    EXPECT_EQ(count, 2);
}

TEST_F(IFCGeneratorTest, ContainsUnitsAndContext) {
    std::string ifc = gen.generate_string(MINIMAL_PLAN);
    EXPECT_NE(ifc.find("IFCSIUNIT"), std::string::npos);
    EXPECT_NE(ifc.find("IFCUNITASSIGNMENT"), std::string::npos);
    EXPECT_NE(ifc.find("IFCGEOMETRICREPRESENTATIONCONTEXT"), std::string::npos);
}

TEST_F(IFCGeneratorTest, GenerateFileSuccess) {
    std::string path = tmp_dir + "/test_model.ifc";
    int rc = gen.generate(MINIMAL_PLAN, path);
    EXPECT_EQ(rc, 0);
    EXPECT_TRUE(fs::exists(path));
    EXPECT_GT(fs::file_size(path), 0u);
}

TEST_F(IFCGeneratorTest, GenerateFileContentMatchesString) {
    std::string path = tmp_dir + "/test_match.ifc";
    gen.generate(MINIMAL_PLAN, path);

    std::ifstream ifs(path);
    std::string file_content((std::istreambuf_iterator<char>(ifs)),
                              std::istreambuf_iterator<char>());

    // Generate fresh string (new instance to reset state)
    promptbim::IFCGenerator gen2;
    std::string str_content = gen2.generate_string(MINIMAL_PLAN);

    EXPECT_EQ(file_content, str_content);
}

TEST_F(IFCGeneratorTest, InvalidJsonReturnsEmpty) {
    std::string ifc = gen.generate_string("{invalid json");
    EXPECT_TRUE(ifc.empty());
}

TEST_F(IFCGeneratorTest, InvalidJsonFileReturnsError) {
    std::string path = tmp_dir + "/bad.ifc";
    int rc = gen.generate("{invalid", path);
    EXPECT_EQ(rc, -1);
}

TEST_F(IFCGeneratorTest, CABIPlanFromJson) {
    PBPlan* plan = pb_plan_from_json(MINIMAL_PLAN);
    ASSERT_NE(plan, nullptr);

    char* json_out = pb_plan_to_json(plan);
    ASSERT_NE(json_out, nullptr);
    EXPECT_NE(std::string(json_out).find("Test Building"), std::string::npos);

    pb_free_string(json_out);
    pb_plan_free(plan);
}

TEST_F(IFCGeneratorTest, CABIPlanFromJsonNull) {
    PBPlan* plan = pb_plan_from_json(nullptr);
    EXPECT_EQ(plan, nullptr);
}

TEST_F(IFCGeneratorTest, CABIPlanFromJsonInvalid) {
    PBPlan* plan = pb_plan_from_json("{bad json");
    EXPECT_EQ(plan, nullptr);
}

TEST_F(IFCGeneratorTest, CABIGenerateIfc) {
    PBPlan* plan = pb_plan_from_json(MINIMAL_PLAN);
    ASSERT_NE(plan, nullptr);

    std::string path = tmp_dir + "/cabi_test.ifc";
    int rc = pb_generate_ifc(plan, path.c_str());
    EXPECT_EQ(rc, 0);
    EXPECT_TRUE(fs::exists(path));

    pb_plan_free(plan);
}

TEST_F(IFCGeneratorTest, CABIGenerateIfcNullArgs) {
    EXPECT_EQ(pb_generate_ifc(nullptr, "/tmp/x.ifc"), -1);

    PBPlan* plan = pb_plan_from_json(MINIMAL_PLAN);
    EXPECT_EQ(pb_generate_ifc(plan, nullptr), -1);
    pb_plan_free(plan);
}

TEST_F(IFCGeneratorTest, VersionInHeader) {
    std::string ifc = gen.generate_string(MINIMAL_PLAN);
    EXPECT_NE(ifc.find("libpromptbim"), std::string::npos);
    EXPECT_NE(ifc.find(pb_version()), std::string::npos);
}
