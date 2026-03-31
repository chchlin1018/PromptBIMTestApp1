// test_binding.cpp — Test that bim_core C++ API is usable (integration test)
// This tests the C++ layer that pybind11 would bind to
#include <gtest/gtest.h>
#include "BIMEntity.h"
#include "BIMSceneGraph.h"
#include "AgentBridge.h"
#include "GeometryEngine.h"
#include "PropertyManager.h"
#include "CostCalculator.h"
#include <nlohmann/json.hpp>

using namespace bim;

TEST(BindingTest, FullWorkflow) {
    // Simulate what Python would do via bim_core module

    // 1. Create scene graph
    BIMSceneGraph sg;

    // 2. Create and add entities
    BIMEntity chiller("ch-01", EntityType::Chiller, "Chiller 1");
    chiller.setPosition({0.0, 0.0, 0.0});
    chiller.setDimensions({3.0, 2.0, 2.5});
    chiller.setProperty("cost", "2500000");
    chiller.setProperty("capacity_kw", "500");
    sg.addEntity(chiller);

    BIMEntity pump("pump-01", EntityType::Pump, "Pump 1");
    pump.setPosition({5.0, 0.0, 0.0});
    pump.setDimensions({1.0, 0.8, 0.6});
    pump.setProperty("cost", "180000");
    sg.addEntity(pump);

    BIMEntity pipe("pipe-01", EntityType::Pipe, "Pipe 1");
    pipe.setPosition({2.5, 0.0, 0.0});
    pipe.setDimensions({5.0, 0.1, 0.1}); // 5m length
    sg.addEntity(pipe);

    EXPECT_EQ(sg.entityCount(), 3);

    // 3. Use AgentBridge
    AgentBridge bridge(sg);
    auto r = bridge.queryByType("Chiller");
    EXPECT_TRUE(r.success);

    r = bridge.moveEntity("ch-01", {10.0, 0.0, 0.0});
    EXPECT_TRUE(r.success);

    r = bridge.connectEntities("ch-01", "pump-01");
    EXPECT_TRUE(r.success);

    // 4. Test GeometryEngine
    bool collision = GeometryEngine::checkCollision(
        {0, 0, 0}, {2, 2, 2},
        {1, 1, 1}, {2, 2, 2}
    );
    EXPECT_TRUE(collision);

    bool noCollision = GeometryEngine::checkCollision(
        {0, 0, 0}, {1, 1, 1},
        {10, 10, 10}, {1, 1, 1}
    );
    EXPECT_FALSE(noCollision);

    double vol = GeometryEngine::boxVolume({3.0, 2.0, 2.5});
    EXPECT_NEAR(vol, 15.0, 1e-9);

    // 5. Test PropertyManager
    PropertyManager props;
    EXPECT_GT(props.materialCount(), 0);
    auto mat = props.getMaterial("concrete_rc");
    ASSERT_TRUE(mat.has_value());
    EXPECT_EQ(mat->name, "RC Concrete");
    EXPECT_GT(mat->costPerUnit, 0.0);

    auto defaults = props.getDefaultProperties(EntityType::Chiller);
    EXPECT_FALSE(defaults.empty());
    EXPECT_EQ(defaults["capacity_kw"], "500");

    // 6. Test CostCalculator
    CostCalculator calc(props);
    auto allEntities = sg.allEntities();
    auto items = calc.calculateAll(allEntities);
    EXPECT_EQ(items.size(), 3u);

    auto summary = calc.summarize(items, 1000.0);
    EXPECT_GT(summary.totalCost, 0.0);
    EXPECT_GT(summary.costPerSqm, 0.0);
    EXPECT_EQ(summary.currency, "NT$");

    // 7. JSON serialization round-trip
    std::string sceneJson = sg.toJson();
    auto sg2 = BIMSceneGraph::fromJson(sceneJson);
    EXPECT_EQ(sg2.entityCount(), 3);

    // 8. Cost summary JSON
    std::string costJson = CostCalculator::toJson(summary);
    auto cj = nlohmann::json::parse(costJson);
    EXPECT_GT(cj["total"].get<double>(), 0.0);
}

TEST(BindingTest, GeometryPolygon) {
    std::vector<Vec3> triangle = {{0, 0, 0}, {4, 0, 0}, {0, 3, 0}};
    double area = GeometryEngine::polygonArea(triangle);
    EXPECT_NEAR(area, 6.0, 1e-9);

    Vec3 centroid = GeometryEngine::polygonCentroid(triangle);
    EXPECT_NEAR(centroid.x, 4.0 / 3.0, 1e-9);
    EXPECT_NEAR(centroid.y, 1.0, 1e-9);
}

TEST(BindingTest, GeometryCylinder) {
    double vol = GeometryEngine::cylinderVolume(1.0, 10.0);
    EXPECT_NEAR(vol, M_PI * 10.0, 1e-6);

    double sa = GeometryEngine::cylinderSurfaceArea(1.0, 10.0);
    EXPECT_NEAR(sa, 2.0 * M_PI * 1.0 * 11.0, 1e-6);
}

TEST(BindingTest, CollisionDetection) {
    std::vector<std::tuple<std::string, Vec3, Vec3>> entities = {
        {"a", {0, 0, 0}, {2, 2, 2}},
        {"b", {1, 0, 0}, {2, 2, 2}},  // overlaps with a
        {"c", {10, 0, 0}, {1, 1, 1}}  // no overlap
    };
    auto collisions = GeometryEngine::detectCollisions(entities);
    EXPECT_EQ(collisions.size(), 1u);
    EXPECT_EQ(collisions[0].first, "a");
    EXPECT_EQ(collisions[0].second, "b");
}

TEST(BindingTest, PropertyManagerMaterials) {
    PropertyManager pm;
    auto structural = pm.getMaterialsByCategory("structural");
    EXPECT_GE(structural.size(), 3u); // concrete, steel, rebar

    auto mep = pm.getMaterialsByCategory("mep");
    EXPECT_GE(mep.size(), 3u); // copper, pvc, duct, cable

    double cost = pm.materialCost("concrete_rc", 100.0);
    EXPECT_GT(cost, 0.0);

    // Non-existent material
    double zero = pm.materialCost("nonexist", 100.0);
    EXPECT_DOUBLE_EQ(zero, 0.0);
}

TEST(BindingTest, CostDelta) {
    PropertyManager pm;
    CostCalculator calc(pm);

    CostSummary before{100000, 50000, 30000, 10000, 190000, 190.0, 5, "NT$"};
    CostSummary after{120000, 55000, 30000, 10000, 215000, 215.0, 6, "NT$"};

    auto delta = calc.costDelta(before, after);
    EXPECT_DOUBLE_EQ(delta.structuralCost, 20000.0);
    EXPECT_DOUBLE_EQ(delta.mepCost, 5000.0);
    EXPECT_DOUBLE_EQ(delta.totalCost, 25000.0);
}
