// bim_core pybind11 module — Python binding for C++ BIM core
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "BIMTypes.h"
#include "BIMEntity.h"
#include "BIMSceneGraph.h"
#include "AgentBridge.h"
#include "GeometryEngine.h"
#include "PropertyManager.h"
#include "CostCalculator.h"

namespace py = pybind11;

PYBIND11_MODULE(bim_core, m) {
    m.doc() = "PromptBIM C++ Core — BIM entity, scene graph, agent bridge, geometry, cost";

    // Vec3
    py::class_<bim::Vec3>(m, "Vec3")
        .def(py::init<>())
        .def(py::init<double, double, double>())
        .def_readwrite("x", &bim::Vec3::x)
        .def_readwrite("y", &bim::Vec3::y)
        .def_readwrite("z", &bim::Vec3::z)
        .def("length", &bim::Vec3::length)
        .def("distance_to", &bim::Vec3::distanceTo)
        .def("dot", &bim::Vec3::dot)
        .def("__repr__", [](const bim::Vec3& v) {
            return "Vec3(" + std::to_string(v.x) + ", " + std::to_string(v.y) + ", " + std::to_string(v.z) + ")";
        });

    // EntityType enum
    py::enum_<bim::EntityType>(m, "EntityType")
        .value("Wall", bim::EntityType::Wall)
        .value("Slab", bim::EntityType::Slab)
        .value("Column", bim::EntityType::Column)
        .value("Beam", bim::EntityType::Beam)
        .value("Roof", bim::EntityType::Roof)
        .value("Door", bim::EntityType::Door)
        .value("Window", bim::EntityType::Window)
        .value("Stair", bim::EntityType::Stair)
        .value("Elevator", bim::EntityType::Elevator)
        .value("Ramp", bim::EntityType::Ramp)
        .value("Chiller", bim::EntityType::Chiller)
        .value("CoolingTower", bim::EntityType::CoolingTower)
        .value("AHU", bim::EntityType::AHU)
        .value("Pump", bim::EntityType::Pump)
        .value("Fan", bim::EntityType::Fan)
        .value("Pipe", bim::EntityType::Pipe)
        .value("Duct", bim::EntityType::Duct)
        .value("Cable", bim::EntityType::Cable)
        .value("Valve", bim::EntityType::Valve)
        .value("Sensor", bim::EntityType::Sensor)
        .value("ExhaustStack", bim::EntityType::ExhaustStack)
        .value("Generic", bim::EntityType::Generic);

    // BIMEntity
    py::class_<bim::BIMEntity>(m, "BIMEntity")
        .def(py::init<>())
        .def(py::init<const std::string&, bim::EntityType, const std::string&>())
        .def("id", &bim::BIMEntity::id)
        .def("type", &bim::BIMEntity::type)
        .def("type_name", &bim::BIMEntity::typeName)
        .def("name", &bim::BIMEntity::name)
        .def("position", &bim::BIMEntity::position)
        .def("rotation", &bim::BIMEntity::rotation)
        .def("dimensions", &bim::BIMEntity::dimensions)
        .def("set_position", &bim::BIMEntity::setPosition)
        .def("set_rotation", &bim::BIMEntity::setRotation)
        .def("set_dimensions", &bim::BIMEntity::setDimensions)
        .def("set_property", &bim::BIMEntity::setProperty)
        .def("get_property", &bim::BIMEntity::getProperty, py::arg("key"), py::arg("default_val") = "")
        .def("has_property", &bim::BIMEntity::hasProperty)
        .def("add_connection", &bim::BIMEntity::addConnection)
        .def("remove_connection", &bim::BIMEntity::removeConnection)
        .def("is_connected_to", &bim::BIMEntity::isConnectedTo)
        .def("distance_to", &bim::BIMEntity::distanceTo)
        .def("volume", &bim::BIMEntity::volume)
        .def("surface_area", &bim::BIMEntity::surfaceArea)
        .def("to_json", &bim::BIMEntity::toJson)
        .def_static("from_json", &bim::BIMEntity::fromJson);

    // BIMSceneGraph
    py::class_<bim::BIMSceneGraph>(m, "BIMSceneGraph")
        .def(py::init<>())
        .def("add_entity", &bim::BIMSceneGraph::addEntity)
        .def("remove_entity", &bim::BIMSceneGraph::removeEntity)
        .def("clear", &bim::BIMSceneGraph::clear)
        .def("entity_count", &bim::BIMSceneGraph::entityCount)
        .def("has_entity", &bim::BIMSceneGraph::hasEntity)
        .def("move_entity", &bim::BIMSceneGraph::moveEntity)
        .def("rotate_entity", &bim::BIMSceneGraph::rotateEntity)
        .def("resize_entity", &bim::BIMSceneGraph::resizeEntity)
        .def("connect_entities", &bim::BIMSceneGraph::connectEntities)
        .def("total_cost", &bim::BIMSceneGraph::totalCost)
        .def("pipe_cost", &bim::BIMSceneGraph::pipeCost, py::arg("from_id"), py::arg("to_id"), py::arg("cost_per_meter") = 3500.0)
        .def("to_json", &bim::BIMSceneGraph::toJson)
        .def_static("from_json", &bim::BIMSceneGraph::fromJson)
        .def("scene_info", &bim::BIMSceneGraph::sceneInfo);

    // AgentBridge
    py::class_<bim::ActionResult>(m, "ActionResult")
        .def_readonly("success", &bim::ActionResult::success)
        .def_readonly("message", &bim::ActionResult::message)
        .def_readonly("data", &bim::ActionResult::data);

    py::class_<bim::AgentBridge>(m, "AgentBridge")
        .def(py::init<bim::BIMSceneGraph&>(), py::keep_alive<1, 2>())
        .def("query_by_type", &bim::AgentBridge::queryByType)
        .def("query_by_name", &bim::AgentBridge::queryByName)
        .def("get_position", &bim::AgentBridge::getPosition)
        .def("get_nearby", &bim::AgentBridge::getNearby)
        .def("get_scene_info", &bim::AgentBridge::getSceneInfo)
        .def("move_entity", &bim::AgentBridge::moveEntity)
        .def("rotate_entity", &bim::AgentBridge::rotateEntity)
        .def("resize_entity", &bim::AgentBridge::resizeEntity)
        .def("add_entity", &bim::AgentBridge::addEntity)
        .def("delete_entity", &bim::AgentBridge::deleteEntity)
        .def("connect_entities", &bim::AgentBridge::connectEntities)
        .def("get_cost_delta", &bim::AgentBridge::getCostDelta)
        .def("get_schedule_impact", &bim::AgentBridge::getScheduleImpact)
        .def("execute_json", &bim::AgentBridge::executeJson);

    // GeometryEngine (static methods)
    py::class_<bim::GeometryEngine>(m, "GeometryEngine")
        .def_static("box_volume", &bim::GeometryEngine::boxVolume)
        .def_static("cylinder_volume", &bim::GeometryEngine::cylinderVolume)
        .def_static("sphere_volume", &bim::GeometryEngine::sphereVolume)
        .def_static("box_surface_area", &bim::GeometryEngine::boxSurfaceArea)
        .def_static("cylinder_surface_area", &bim::GeometryEngine::cylinderSurfaceArea)
        .def_static("check_collision", &bim::GeometryEngine::checkCollision)
        .def_static("entity_distance", &bim::GeometryEngine::entityDistance);

    // PropertyManager
    py::class_<bim::MaterialSpec>(m, "MaterialSpec")
        .def(py::init<>())
        .def_readwrite("name", &bim::MaterialSpec::name)
        .def_readwrite("category", &bim::MaterialSpec::category)
        .def_readwrite("density", &bim::MaterialSpec::density)
        .def_readwrite("cost_per_unit", &bim::MaterialSpec::costPerUnit)
        .def_readwrite("unit", &bim::MaterialSpec::unit);

    py::class_<bim::PropertyManager>(m, "PropertyManager")
        .def(py::init<>())
        .def("material_count", &bim::PropertyManager::materialCount)
        .def("material_cost", &bim::PropertyManager::materialCost)
        .def("to_json", &bim::PropertyManager::toJson);

    // CostCalculator
    py::class_<bim::CostSummary>(m, "CostSummary")
        .def_readonly("structural_cost", &bim::CostSummary::structuralCost)
        .def_readonly("mep_cost", &bim::CostSummary::mepCost)
        .def_readonly("finish_cost", &bim::CostSummary::finishCost)
        .def_readonly("other_cost", &bim::CostSummary::otherCost)
        .def_readonly("total_cost", &bim::CostSummary::totalCost)
        .def_readonly("cost_per_sqm", &bim::CostSummary::costPerSqm)
        .def_readonly("item_count", &bim::CostSummary::itemCount)
        .def_readonly("currency", &bim::CostSummary::currency);

    py::class_<bim::CostCalculator>(m, "CostCalculator")
        .def(py::init<const bim::PropertyManager&>(), py::keep_alive<1, 2>())
        .def("pipe_cost", &bim::CostCalculator::pipeCost, py::arg("from_entity"), py::arg("to_entity"), py::arg("cost_per_meter") = 3500.0);
}
