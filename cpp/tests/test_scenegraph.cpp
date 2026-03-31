// test_scenegraph.cpp — BIMSceneGraph node operations tests
#include <gtest/gtest.h>
#include "BIMSceneGraph.h"

using namespace bim;

class SceneGraphTest : public ::testing::Test {
protected:
    void SetUp() override {
        sg.addEntity(BIMEntity("col-A1", EntityType::Column, "Column A1"));
        sg.addEntity(BIMEntity("col-A2", EntityType::Column, "Column A2"));
        sg.addEntity(BIMEntity("wall-01", EntityType::Wall, "North Wall"));
        sg.addEntity(BIMEntity("ch-01", EntityType::Chiller, "Chiller 1"));

        sg.moveEntity("col-A1", {0.0, 0.0, 0.0});
        sg.moveEntity("col-A2", {6.0, 0.0, 0.0});
        sg.moveEntity("wall-01", {3.0, 0.0, 0.0});
        sg.moveEntity("ch-01", {20.0, 0.0, 0.0});
    }
    BIMSceneGraph sg;
};

TEST_F(SceneGraphTest, EntityCount) {
    EXPECT_EQ(sg.entityCount(), 4);
}

TEST_F(SceneGraphTest, AddDuplicate) {
    EXPECT_FALSE(sg.addEntity(BIMEntity("col-A1", EntityType::Column, "Dup")));
    EXPECT_EQ(sg.entityCount(), 4);
}

TEST_F(SceneGraphTest, AddEmptyId) {
    EXPECT_FALSE(sg.addEntity(BIMEntity("", EntityType::Generic, "Empty")));
}

TEST_F(SceneGraphTest, RemoveEntity) {
    EXPECT_TRUE(sg.removeEntity("ch-01"));
    EXPECT_EQ(sg.entityCount(), 3);
    EXPECT_FALSE(sg.hasEntity("ch-01"));
}

TEST_F(SceneGraphTest, RemoveNonexistent) {
    EXPECT_FALSE(sg.removeEntity("nonexist"));
}

TEST_F(SceneGraphTest, FindEntity) {
    auto* e = sg.findEntity("wall-01");
    ASSERT_NE(e, nullptr);
    EXPECT_EQ(e->name(), "North Wall");
    EXPECT_EQ(sg.findEntity("nonexist"), nullptr);
}

TEST_F(SceneGraphTest, QueryByType) {
    auto cols = sg.queryByType(EntityType::Column);
    EXPECT_EQ(cols.size(), 2u);
    auto walls = sg.queryByType("Wall");
    EXPECT_EQ(walls.size(), 1u);
}

TEST_F(SceneGraphTest, QueryByName) {
    auto results = sg.queryByName("Column");
    EXPECT_EQ(results.size(), 2u);
    auto results2 = sg.queryByName("Chiller");
    EXPECT_EQ(results2.size(), 1u);
}

TEST_F(SceneGraphTest, NearbyEntities) {
    auto nearby = sg.nearbyEntities("col-A1", 7.0);
    // col-A2 (6m) and wall-01 (3m) should be within 7m, ch-01 (20m) should not
    EXPECT_EQ(nearby.size(), 2u);
    auto far = sg.nearbyEntities("col-A1", 1.0);
    EXPECT_EQ(far.size(), 0u);
}

TEST_F(SceneGraphTest, MoveEntity) {
    EXPECT_TRUE(sg.moveEntity("col-A1", {10.0, 5.0, 0.0}));
    auto* e = sg.findEntity("col-A1");
    EXPECT_DOUBLE_EQ(e->position().x, 10.0);
    EXPECT_FALSE(sg.moveEntity("nonexist", {0, 0, 0}));
}

TEST_F(SceneGraphTest, RotateEntity) {
    EXPECT_TRUE(sg.rotateEntity("wall-01", {0, 90.0, 0}));
    auto* e = sg.findEntity("wall-01");
    EXPECT_DOUBLE_EQ(e->rotation().y, 90.0);
}

TEST_F(SceneGraphTest, ResizeEntity) {
    EXPECT_TRUE(sg.resizeEntity("wall-01", {10.0, 3.0, 0.2}));
    auto* e = sg.findEntity("wall-01");
    EXPECT_DOUBLE_EQ(e->dimensions().x, 10.0);
}

TEST_F(SceneGraphTest, ConnectEntities) {
    EXPECT_TRUE(sg.connectEntities("col-A1", "col-A2"));
    auto* a = sg.findEntity("col-A1");
    auto* b = sg.findEntity("col-A2");
    EXPECT_TRUE(a->isConnectedTo("col-A2"));
    EXPECT_TRUE(b->isConnectedTo("col-A1"));
    EXPECT_FALSE(sg.connectEntities("col-A1", "nonexist"));
}

TEST_F(SceneGraphTest, TotalCost) {
    auto* ch = sg.findEntity("ch-01");
    ch->setProperty("cost", "2500000");
    EXPECT_DOUBLE_EQ(sg.totalCost(), 2500000.0);
}

TEST_F(SceneGraphTest, PipeCost) {
    // Distance col-A1(0,0,0) to col-A2(6,0,0) = 6m
    double cost = sg.pipeCost("col-A1", "col-A2", 3500.0);
    EXPECT_NEAR(cost, 21000.0, 1e-6);
    EXPECT_DOUBLE_EQ(sg.pipeCost("col-A1", "nonexist"), 0.0);
}

TEST_F(SceneGraphTest, Clear) {
    sg.clear();
    EXPECT_EQ(sg.entityCount(), 0);
}

TEST_F(SceneGraphTest, JsonRoundTrip) {
    std::string json = sg.toJson();
    auto sg2 = BIMSceneGraph::fromJson(json);
    EXPECT_EQ(sg2.entityCount(), 4);
    EXPECT_TRUE(sg2.hasEntity("col-A1"));
    EXPECT_TRUE(sg2.hasEntity("ch-01"));
}

TEST_F(SceneGraphTest, SceneInfo) {
    std::string info = sg.sceneInfo();
    EXPECT_FALSE(info.empty());
    // Should contain entityCount
    EXPECT_NE(info.find("entityCount"), std::string::npos);
}

TEST_F(SceneGraphTest, AllEntities) {
    auto all = sg.allEntities();
    EXPECT_EQ(all.size(), 4u);
}
