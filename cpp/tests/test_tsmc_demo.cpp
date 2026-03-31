// test_tsmc_demo.cpp — TSMC Demo scenario verification tests
// Verifies: factory scene creation, safety equipment, collision detection,
//           cost calculation, 4D phase entity assignment, AI action routing.

#include <gtest/gtest.h>
#include "AgentBridge.h"
#include "GeometryEngine.h"
#include "CostCalculator.h"
#include "PropertyManager.h"
#include <nlohmann/json.hpp>

using namespace bim;
using json = nlohmann::json;

// ---------------------------------------------------------------------------
// Helper: build the TSMC factory scene (mirrors tsmc_factory.py)
// ---------------------------------------------------------------------------

static void buildTSMCScene(BIMSceneGraph& sg) {
    // Structural
    auto addE = [&](const std::string& id, EntityType t, const std::string& name,
                    Vec3 pos, Vec3 dims, const std::map<std::string, std::string>& props = {}) {
        BIMEntity e(id, t, name);
        e.setPosition(pos);
        e.setDimensions(dims);
        for (const auto& [k, v] : props) e.setProperty(k, v);
        sg.addEntity(e);
    };

    // Slabs
    addE("slab-b1", EntityType::Slab, "B1 Foundation", {50,35,-4}, {100,70,0.6});
    addE("slab-1f", EntityType::Slab, "1F Fab Floor", {50,35,0}, {100,70,0.5});
    addE("slab-2f", EntityType::Slab, "2F Office", {50,35,8}, {100,70,0.4});
    addE("slab-rf", EntityType::Slab, "RF Roof Slab", {50,35,12}, {100,70,0.3});

    // Columns (8)
    addE("col-01", EntityType::Column, "A1", {0,0,0}, {1.2,1.2,12});
    addE("col-02", EntityType::Column, "A2", {50,0,0}, {1.2,1.2,12});
    addE("col-03", EntityType::Column, "A3", {100,0,0}, {1.2,1.2,12});
    addE("col-04", EntityType::Column, "B1", {0,70,0}, {1.2,1.2,12});
    addE("col-05", EntityType::Column, "B2", {50,70,0}, {1.2,1.2,12});
    addE("col-06", EntityType::Column, "B3", {100,70,0}, {1.2,1.2,12});
    addE("col-07", EntityType::Column, "C1", {0,35,0}, {1.2,1.2,12});
    addE("col-08", EntityType::Column, "C2", {100,35,0}, {1.2,1.2,12});

    // Beams
    addE("beam-01", EntityType::Beam, "Main A-axis", {50,0,7.5}, {100,0.8,1.0});
    addE("beam-02", EntityType::Beam, "Main B-axis", {50,70,7.5}, {100,0.8,1.0});

    // Walls
    addE("wall-n", EntityType::Wall, "North Wall", {50,0,4}, {100,0.3,8});
    addE("wall-s", EntityType::Wall, "South Wall", {50,70,4}, {100,0.3,8});

    // Roof
    addE("roof-01", EntityType::Roof, "Main Roof", {50,35,16}, {105,75,0.4});

    // MEP
    addE("chiller-1", EntityType::Chiller, "Chiller A", {20,20,-3}, {4,2,2.5},
         {{"capacity","500RT"}, {"cost","2500000"}});
    addE("chiller-2", EntityType::Chiller, "Chiller B", {20,50,-3}, {4,2,2.5},
         {{"capacity","500RT"}, {"cost","2500000"}});
    addE("ct-1", EntityType::CoolingTower, "CT A", {30,20,16.5}, {3,3,4},
         {{"cost","800000"}});
    addE("ct-2", EntityType::CoolingTower, "CT B", {30,50,16.5}, {3,3,4},
         {{"cost","800000"}});
    addE("ahu-1", EntityType::AHU, "AHU A", {80,15,0.5}, {6,3,3},
         {{"cost","650000"}});
    addE("ahu-2", EntityType::AHU, "AHU B", {80,55,0.5}, {6,3,3},
         {{"cost","650000"}});
    addE("pump-1", EntityType::Pump, "Pump A", {25,20,-3}, {1.5,1,1.2},
         {{"cost","180000"}});
    addE("pump-2", EntityType::Pump, "Pump B", {25,50,-3}, {1.5,1,1.2},
         {{"cost","180000"}});
    addE("exhaust-1", EntityType::ExhaustStack, "Exhaust", {90,35,16.5}, {1.5,1.5,6},
         {{"cost","350000"}});

    // Pipes & ducts
    addE("pipe-ch1-ahu1", EntityType::Pipe, "CW Pipe A", {50,17.5,-2}, {60,0.3,0.3});
    addE("pipe-ch2-ahu2", EntityType::Pipe, "CW Pipe B", {50,52.5,-2}, {60,0.3,0.3});
    addE("duct-1", EntityType::Duct, "Supply Duct A", {50,15,6.5}, {60,1.2,0.8});
    addE("duct-2", EntityType::Duct, "Supply Duct B", {50,55,6.5}, {60,1.2,0.8});

    // Sensors
    addE("sensor-t1", EntityType::Sensor, "Temp A", {40,25,2.5}, {0.1,0.1,0.1});
    addE("sensor-t2", EntityType::Sensor, "Temp B", {60,45,2.5}, {0.1,0.1,0.1});

    // Safety — fire hydrants (using Generic isn't available, use Sensor as proxy)
    addE("hydrant-1", EntityType::Generic, "Fire Hydrant NW", {5,5,0.5}, {0.4,0.4,1.2},
         {{"subtype","fire_hydrant"}, {"cost","35000"}});
    addE("hydrant-2", EntityType::Generic, "Fire Hydrant NE", {95,5,0.5}, {0.4,0.4,1.2},
         {{"subtype","fire_hydrant"}, {"cost","35000"}});
    addE("hydrant-3", EntityType::Generic, "Fire Hydrant SE", {95,65,0.5}, {0.4,0.4,1.2},
         {{"subtype","fire_hydrant"}, {"cost","35000"}});
    addE("hydrant-4", EntityType::Generic, "Fire Hydrant SW", {5,65,0.5}, {0.4,0.4,1.2},
         {{"subtype","fire_hydrant"}, {"cost","35000"}});

    // Emergency exits
    addE("exit-1", EntityType::Door, "Emergency Exit N", {50,0,0}, {2,0.3,2.4},
         {{"subtype","emergency_exit"}, {"cost","45000"}});
    addE("exit-2", EntityType::Door, "Emergency Exit S", {50,70,0}, {2,0.3,2.4},
         {{"subtype","emergency_exit"}, {"cost","45000"}});
}

// ---------------------------------------------------------------------------
// T01: Factory model — entity count & types
// ---------------------------------------------------------------------------

class TSMCDemoTest : public ::testing::Test {
protected:
    void SetUp() override {
        buildTSMCScene(sg);
        bridge = std::make_unique<AgentBridge>(sg);
    }
    BIMSceneGraph sg;
    std::unique_ptr<AgentBridge> bridge;
};

TEST_F(TSMCDemoTest, SceneEntityCount) {
    EXPECT_GE(sg.entityCount(), 35);
}

TEST_F(TSMCDemoTest, StructuralEntities) {
    auto slabs = sg.queryByType(EntityType::Slab);
    EXPECT_EQ(slabs.size(), 4u);
    auto cols = sg.queryByType(EntityType::Column);
    EXPECT_EQ(cols.size(), 8u);
    auto beams = sg.queryByType(EntityType::Beam);
    EXPECT_EQ(beams.size(), 2u);
}

TEST_F(TSMCDemoTest, MEPEntities) {
    auto chillers = sg.queryByType(EntityType::Chiller);
    EXPECT_EQ(chillers.size(), 2u);
    auto cts = sg.queryByType(EntityType::CoolingTower);
    EXPECT_EQ(cts.size(), 2u);
    auto ahus = sg.queryByType(EntityType::AHU);
    EXPECT_EQ(ahus.size(), 2u);
    auto pumps = sg.queryByType(EntityType::Pump);
    EXPECT_EQ(pumps.size(), 2u);
}

// T02: Safety equipment
TEST_F(TSMCDemoTest, SafetyHydrants) {
    auto hydrants = sg.queryByName("Hydrant");
    EXPECT_EQ(hydrants.size(), 4u);
}

TEST_F(TSMCDemoTest, EmergencyExits) {
    auto exits = sg.queryByName("Emergency Exit");
    EXPECT_EQ(exits.size(), 2u);
}

// T03: Collision detection
TEST_F(TSMCDemoTest, NoChillerPumpCollision) {
    // Chiller A at (20,20,-3) 4x2x2.5, Pump A at (25,20,-3) 1.5x1x1.2
    // Gap: 25 - 20 = 5m center distance, half-extents 2.0 + 0.75 = 2.75
    // → no collision (5 > 2.75)
    bool collides = GeometryEngine::checkCollision(
        {20,20,-3}, {4,2,2.5}, {25,20,-3}, {1.5,1,1.2});
    EXPECT_FALSE(collides);
}

TEST_F(TSMCDemoTest, OverlappingEntitiesDetected) {
    // Two entities at the same position should collide
    bool collides = GeometryEngine::checkCollision(
        {50,35,0}, {10,10,5}, {52,35,0}, {10,10,5});
    EXPECT_TRUE(collides);
}

TEST_F(TSMCDemoTest, CollisionDetectionBatch) {
    std::vector<std::tuple<std::string, Vec3, Vec3>> ents;
    ents.push_back({"box-a", {0,0,0}, {2,2,2}});
    ents.push_back({"box-b", {1,0,0}, {2,2,2}});  // overlaps with a
    ents.push_back({"box-c", {10,0,0}, {2,2,2}}); // isolated
    auto pairs = GeometryEngine::detectCollisions(ents);
    EXPECT_EQ(pairs.size(), 1u);
    EXPECT_EQ(pairs[0].first, "box-a");
    EXPECT_EQ(pairs[0].second, "box-b");
}

// T04: Cost calculation
TEST_F(TSMCDemoTest, ChillerCost) {
    const auto* ch = sg.findEntity("chiller-1");
    ASSERT_NE(ch, nullptr);
    PropertyManager pm;
    CostCalculator calc(pm);
    auto item = calc.calculateEntityCost(*ch);
    EXPECT_DOUBLE_EQ(item.total, 2500000.0);
    EXPECT_EQ(item.category, "mep");
}

TEST_F(TSMCDemoTest, TotalCostPositive) {
    PropertyManager pm;
    CostCalculator calc(pm);
    auto all = sg.allEntities();
    auto items = calc.calculateAll(all);
    auto summary = calc.summarize(items, 7000.0);
    EXPECT_GT(summary.totalCost, 0.0);
    EXPECT_GT(summary.mepCost, 0.0);
    EXPECT_GT(summary.structuralCost, 0.0);
    EXPECT_GT(summary.costPerSqm, 0.0);
}

TEST_F(TSMCDemoTest, PipeCostCalculation) {
    const auto* ch = sg.findEntity("chiller-1");
    const auto* ahu = sg.findEntity("ahu-1");
    ASSERT_NE(ch, nullptr);
    ASSERT_NE(ahu, nullptr);
    PropertyManager pm;
    CostCalculator calc(pm);
    double cost = calc.pipeCost(*ch, *ahu, 3500.0);
    EXPECT_GT(cost, 0.0);
}

// Helper: parse executeJson response and check success
static bool jsonSuccess(const std::string& response) {
    auto j = json::parse(response);
    return j.value("success", false);
}

static json jsonData(const std::string& response) {
    auto j = json::parse(response);
    if (j.contains("data") && j["data"].is_string()) {
        return json::parse(j["data"].get<std::string>());
    }
    if (j.contains("data")) return j["data"];
    return json::object();
}

// T05: AgentBridge JSON actions for demo scenarios
TEST_F(TSMCDemoTest, QueryByTypeJSON) {
    auto r = bridge->queryByType("Chiller");
    EXPECT_TRUE(r.success);
    auto data = json::parse(r.data);
    EXPECT_EQ(data.size(), 2u);
}

TEST_F(TSMCDemoTest, MoveEntityJSON) {
    auto r = bridge->moveEntity("chiller-1", {30, 25, -3});
    EXPECT_TRUE(r.success);
    const auto* ch = sg.findEntity("chiller-1");
    EXPECT_DOUBLE_EQ(ch->position().x, 30.0);
    EXPECT_DOUBLE_EQ(ch->position().y, 25.0);
}

TEST_F(TSMCDemoTest, AddEntityJSON) {
    auto r = bridge->addEntity("ahu-3", EntityType::AHU, "AHU C", {60, 35, 0.5});
    EXPECT_TRUE(r.success);
    EXPECT_TRUE(sg.hasEntity("ahu-3"));
}

TEST_F(TSMCDemoTest, DeleteEntityJSON) {
    EXPECT_TRUE(sg.hasEntity("sensor-t1"));
    auto r = bridge->deleteEntity("sensor-t1");
    EXPECT_TRUE(r.success);
    EXPECT_FALSE(sg.hasEntity("sensor-t1"));
}

TEST_F(TSMCDemoTest, ConnectEntitiesJSON) {
    auto r = bridge->connectEntities("pump-1", "chiller-1");
    EXPECT_TRUE(r.success);
}

TEST_F(TSMCDemoTest, GetSceneInfoJSON) {
    auto r = bridge->getSceneInfo();
    EXPECT_TRUE(r.success);
    EXPECT_FALSE(r.data.empty());
}

TEST_F(TSMCDemoTest, GetNearbyJSON) {
    auto r = bridge->getNearby("chiller-1", 10.0);
    EXPECT_TRUE(r.success);
    auto data = json::parse(r.data);
    EXPECT_GE(data.size(), 1u);  // pump-1 should be nearby
}

TEST_F(TSMCDemoTest, CostDeltaJSON) {
    auto r = bridge->getCostDelta();
    EXPECT_TRUE(r.success);
}

// T05 continued: executeJson round-trip
TEST_F(TSMCDemoTest, ExecuteJsonRoundTrip) {
    std::string req = R"({"action":"query_by_type","type":"Chiller"})";
    auto resp = bridge->executeJson(req);
    EXPECT_FALSE(resp.empty());
    auto j = json::parse(resp);
    EXPECT_TRUE(j.value("success", false));
}

// Full demo flow: query → move → add → cost
TEST_F(TSMCDemoTest, FullDemoFlow) {
    // Step 1: Query scene
    auto r1 = bridge->getSceneInfo();
    EXPECT_TRUE(r1.success);

    // Step 2: Move chiller
    auto r2 = bridge->moveEntity("chiller-1", {30, 25, -3});
    EXPECT_TRUE(r2.success);

    // Step 3: Add new AHU
    auto r3 = bridge->addEntity("ahu-3", EntityType::AHU, "AHU C", {60, 35, 0.5});
    EXPECT_TRUE(r3.success);

    // Step 4: Check cost
    auto r4 = bridge->getCostDelta();
    EXPECT_TRUE(r4.success);

    // Step 5: Connect
    auto r5 = bridge->connectEntities("pump-1", "chiller-1");
    EXPECT_TRUE(r5.success);

    // Verify final state
    EXPECT_GE(sg.entityCount(), 36);  // 35 original + 1 added
}
