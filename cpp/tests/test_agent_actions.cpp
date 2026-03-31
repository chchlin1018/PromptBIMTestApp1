// test_agent_actions.cpp — AgentBridge 13 actions test
#include <gtest/gtest.h>
#include "AgentBridge.h"
#include <nlohmann/json.hpp>

using namespace bim;

class AgentBridgeTest : public ::testing::Test {
protected:
    void SetUp() override {
        sg.addEntity(BIMEntity("ch-01", EntityType::Chiller, "Chiller 1"));
        sg.moveEntity("ch-01", {0.0, 0.0, 0.0});
        sg.addEntity(BIMEntity("pump-01", EntityType::Pump, "Pump 1"));
        sg.moveEntity("pump-01", {5.0, 0.0, 0.0});
        sg.addEntity(BIMEntity("col-01", EntityType::Column, "Column A1"));
        sg.moveEntity("col-01", {10.0, 0.0, 0.0});
        auto* ch = sg.findEntity("ch-01");
        ch->setProperty("cost", "2500000");
        bridge = std::make_unique<AgentBridge>(sg);
    }
    BIMSceneGraph sg;
    std::unique_ptr<AgentBridge> bridge;
};

// === Query Actions (5) ===

TEST_F(AgentBridgeTest, QueryByType) {
    auto r = bridge->queryByType("Chiller");
    EXPECT_TRUE(r.success);
    auto data = nlohmann::json::parse(r.data);
    EXPECT_EQ(data.size(), 1u);
    EXPECT_EQ(data[0]["name"], "Chiller 1");
}

TEST_F(AgentBridgeTest, QueryByName) {
    auto r = bridge->queryByName("Pump");
    EXPECT_TRUE(r.success);
    auto data = nlohmann::json::parse(r.data);
    EXPECT_EQ(data.size(), 1u);
}

TEST_F(AgentBridgeTest, GetPosition) {
    auto r = bridge->getPosition("ch-01");
    EXPECT_TRUE(r.success);
    auto data = nlohmann::json::parse(r.data);
    EXPECT_EQ(data["id"], "ch-01");

    auto r2 = bridge->getPosition("nonexist");
    EXPECT_FALSE(r2.success);
}

TEST_F(AgentBridgeTest, GetNearby) {
    auto r = bridge->getNearby("ch-01", 6.0);
    EXPECT_TRUE(r.success);
    auto data = nlohmann::json::parse(r.data);
    EXPECT_EQ(data.size(), 1u); // pump-01 at 5m
}

TEST_F(AgentBridgeTest, GetSceneInfo) {
    auto r = bridge->getSceneInfo();
    EXPECT_TRUE(r.success);
    auto data = nlohmann::json::parse(r.data);
    EXPECT_EQ(data["entityCount"], 3);
}

// === Operate Actions (6) ===

TEST_F(AgentBridgeTest, MoveEntity) {
    auto r = bridge->moveEntity("ch-01", {15.0, 0.0, 0.0});
    EXPECT_TRUE(r.success);
    auto* e = sg.findEntity("ch-01");
    EXPECT_DOUBLE_EQ(e->position().x, 15.0);

    auto r2 = bridge->moveEntity("nonexist", {0, 0, 0});
    EXPECT_FALSE(r2.success);
}

TEST_F(AgentBridgeTest, RotateEntity) {
    auto r = bridge->rotateEntity("ch-01", {0, 45.0, 0});
    EXPECT_TRUE(r.success);
}

TEST_F(AgentBridgeTest, ResizeEntity) {
    auto r = bridge->resizeEntity("ch-01", {3.0, 2.0, 2.5});
    EXPECT_TRUE(r.success);
}

TEST_F(AgentBridgeTest, AddEntity) {
    auto r = bridge->addEntity("fan-01", EntityType::Fan, "Fan 1", {8.0, 0.0, 3.0});
    EXPECT_TRUE(r.success);
    EXPECT_EQ(sg.entityCount(), 4);
    EXPECT_TRUE(sg.hasEntity("fan-01"));

    // Duplicate
    auto r2 = bridge->addEntity("fan-01", EntityType::Fan, "Fan Dup", {0, 0, 0});
    EXPECT_FALSE(r2.success);
}

TEST_F(AgentBridgeTest, DeleteEntity) {
    auto r = bridge->deleteEntity("pump-01");
    EXPECT_TRUE(r.success);
    EXPECT_EQ(sg.entityCount(), 2);

    auto r2 = bridge->deleteEntity("nonexist");
    EXPECT_FALSE(r2.success);
}

TEST_F(AgentBridgeTest, ConnectEntities) {
    auto r = bridge->connectEntities("ch-01", "pump-01");
    EXPECT_TRUE(r.success);
    auto* ch = sg.findEntity("ch-01");
    EXPECT_TRUE(ch->isConnectedTo("pump-01"));
}

// === Cost/Schedule Actions (2) ===

TEST_F(AgentBridgeTest, GetCostDelta) {
    // Initial baseline captured in SetUp
    auto* pump = sg.findEntity("pump-01");
    pump->setProperty("cost", "180000");
    auto r = bridge->getCostDelta();
    EXPECT_TRUE(r.success);
    auto data = nlohmann::json::parse(r.data);
    EXPECT_GT(data["delta"].get<double>(), 0.0);
}

TEST_F(AgentBridgeTest, GetScheduleImpact) {
    auto r = bridge->getScheduleImpact();
    EXPECT_TRUE(r.success);
    auto data = nlohmann::json::parse(r.data);
    EXPECT_EQ(data["entityCount"], 3);
    EXPECT_EQ(data["impact"], "low");
}

// === JSON Interface ===

TEST_F(AgentBridgeTest, ExecuteJsonQueryByType) {
    std::string req = R"({"action": "query_by_type", "type": "Pump"})";
    std::string resp = bridge->executeJson(req);
    auto j = nlohmann::json::parse(resp);
    EXPECT_TRUE(j["success"]);
}

TEST_F(AgentBridgeTest, ExecuteJsonMove) {
    std::string req = R"({"action": "move", "id": "ch-01", "position": [20.0, 0.0, 0.0]})";
    std::string resp = bridge->executeJson(req);
    auto j = nlohmann::json::parse(resp);
    EXPECT_TRUE(j["success"]);
}

TEST_F(AgentBridgeTest, ExecuteJsonAdd) {
    std::string req = R"({"action": "add", "id": "valve-01", "type": "Valve", "name": "Valve 1", "position": [1.0, 2.0, 3.0]})";
    std::string resp = bridge->executeJson(req);
    auto j = nlohmann::json::parse(resp);
    EXPECT_TRUE(j["success"]);
    EXPECT_TRUE(sg.hasEntity("valve-01"));
}

TEST_F(AgentBridgeTest, ExecuteJsonInvalid) {
    std::string req = R"({"action": "bogus"})";
    std::string resp = bridge->executeJson(req);
    auto j = nlohmann::json::parse(resp);
    EXPECT_FALSE(j["success"]);
}

TEST_F(AgentBridgeTest, ExecuteJsonMalformed) {
    std::string resp = bridge->executeJson("not json");
    auto j = nlohmann::json::parse(resp);
    EXPECT_FALSE(j["success"]);
}
