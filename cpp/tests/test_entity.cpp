// test_entity.cpp — BIMEntity create/query/delete tests
#include <gtest/gtest.h>
#include "BIMEntity.h"
#include "BIMTypes.h"

using namespace bim;

TEST(BIMEntityTest, CreateDefault) {
    BIMEntity e;
    EXPECT_TRUE(e.id().empty());
    EXPECT_EQ(e.type(), EntityType::Generic);
    EXPECT_EQ(e.name(), "");
}

TEST(BIMEntityTest, CreateWithParams) {
    BIMEntity e("wall-001", EntityType::Wall, "Main Wall");
    EXPECT_EQ(e.id(), "wall-001");
    EXPECT_EQ(e.type(), EntityType::Wall);
    EXPECT_EQ(e.typeName(), "Wall");
    EXPECT_EQ(e.name(), "Main Wall");
}

TEST(BIMEntityTest, SetPosition) {
    BIMEntity e("col-001", EntityType::Column, "Column A1");
    e.setPosition({10.0, 0.0, 5.0});
    EXPECT_DOUBLE_EQ(e.position().x, 10.0);
    EXPECT_DOUBLE_EQ(e.position().y, 0.0);
    EXPECT_DOUBLE_EQ(e.position().z, 5.0);
}

TEST(BIMEntityTest, SetDimensions) {
    BIMEntity e("slab-001", EntityType::Slab, "Floor Slab");
    e.setDimensions({20.0, 15.0, 0.15});
    EXPECT_DOUBLE_EQ(e.dimensions().x, 20.0);
    EXPECT_DOUBLE_EQ(e.dimensions().z, 0.15);
}

TEST(BIMEntityTest, Properties) {
    BIMEntity e("ch-001", EntityType::Chiller, "Chiller 1");
    e.setProperty("capacity_kw", "500");
    e.setProperty("cost", "2500000");
    EXPECT_TRUE(e.hasProperty("capacity_kw"));
    EXPECT_EQ(e.getProperty("capacity_kw"), "500");
    EXPECT_EQ(e.getProperty("missing", "default"), "default");
    e.removeProperty("capacity_kw");
    EXPECT_FALSE(e.hasProperty("capacity_kw"));
}

TEST(BIMEntityTest, Connections) {
    BIMEntity e("pump-001", EntityType::Pump, "Pump 1");
    e.addConnection("ch-001");
    e.addConnection("pipe-001");
    EXPECT_TRUE(e.isConnectedTo("ch-001"));
    EXPECT_TRUE(e.isConnectedTo("pipe-001"));
    EXPECT_FALSE(e.isConnectedTo("unknown"));
    e.removeConnection("ch-001");
    EXPECT_FALSE(e.isConnectedTo("ch-001"));
    // Duplicate add should not create duplicates
    e.addConnection("pipe-001");
    EXPECT_EQ(e.connections().size(), 1u);
}

TEST(BIMEntityTest, Distance) {
    BIMEntity a("a", EntityType::Column, "A");
    BIMEntity b("b", EntityType::Column, "B");
    a.setPosition({0.0, 0.0, 0.0});
    b.setPosition({3.0, 4.0, 0.0});
    EXPECT_NEAR(a.distanceTo(b), 5.0, 1e-9);
}

TEST(BIMEntityTest, Volume) {
    BIMEntity e("wall-001", EntityType::Wall, "Wall");
    e.setDimensions({10.0, 3.0, 0.2});
    EXPECT_NEAR(e.volume(), 6.0, 1e-9);
}

TEST(BIMEntityTest, SurfaceArea) {
    BIMEntity e("box", EntityType::Generic, "Box");
    e.setDimensions({2.0, 3.0, 4.0});
    // 2*(2*3 + 3*4 + 2*4) = 2*(6+12+8) = 52
    EXPECT_NEAR(e.surfaceArea(), 52.0, 1e-9);
}

TEST(BIMEntityTest, JsonRoundTrip) {
    BIMEntity e("beam-001", EntityType::Beam, "Main Beam");
    e.setPosition({5.0, 0.0, 3.0});
    e.setDimensions({8.0, 0.6, 0.3});
    e.setProperty("material", "concrete_rc");
    e.addConnection("col-001");

    std::string json = e.toJson();
    BIMEntity e2 = BIMEntity::fromJson(json);

    EXPECT_EQ(e2.id(), "beam-001");
    EXPECT_EQ(e2.type(), EntityType::Beam);
    EXPECT_EQ(e2.name(), "Main Beam");
    EXPECT_NEAR(e2.position().x, 5.0, 1e-9);
    EXPECT_EQ(e2.getProperty("material"), "concrete_rc");
    EXPECT_TRUE(e2.isConnectedTo("col-001"));
}

TEST(BIMEntityTest, AllEntityTypes) {
    // Verify all 22 entity types round-trip through string conversion
    for (int i = 0; i < ENTITY_TYPE_COUNT; ++i) {
        EntityType t = static_cast<EntityType>(i);
        std::string name = entityTypeName(t);
        EXPECT_FALSE(name.empty());
        EntityType t2 = entityTypeFromString(name);
        EXPECT_EQ(t, t2) << "Failed for type: " << name;
    }
}

TEST(Vec3Test, Operations) {
    Vec3 a{1.0, 2.0, 3.0};
    Vec3 b{4.0, 5.0, 6.0};
    Vec3 sum = a + b;
    EXPECT_DOUBLE_EQ(sum.x, 5.0);
    EXPECT_DOUBLE_EQ(sum.y, 7.0);
    EXPECT_DOUBLE_EQ(sum.z, 9.0);

    Vec3 diff = b - a;
    EXPECT_DOUBLE_EQ(diff.x, 3.0);

    Vec3 scaled = a * 2.0;
    EXPECT_DOUBLE_EQ(scaled.x, 2.0);

    EXPECT_DOUBLE_EQ(a.dot(b), 32.0);  // 1*4 + 2*5 + 3*6
    EXPECT_NEAR((Vec3{3.0, 4.0, 0.0}).length(), 5.0, 1e-9);
}
