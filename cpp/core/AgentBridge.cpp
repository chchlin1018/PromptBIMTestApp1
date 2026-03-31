#include "AgentBridge.h"
#include <nlohmann/json.hpp>
#include <sstream>

namespace bim {

AgentBridge::AgentBridge(BIMSceneGraph& scene)
    : m_scene(scene), m_lastTotalCost(scene.totalCost()) {}

ActionResult AgentBridge::execute(const ActionRequest& req) {
    switch (req.action) {
        case AgentAction::QueryByType:      return queryByType(req.queryString);
        case AgentAction::QueryByName:      return queryByName(req.queryString);
        case AgentAction::GetPosition:      return getPosition(req.entityId);
        case AgentAction::GetNearby:        return getNearby(req.entityId, req.radius);
        case AgentAction::GetSceneInfo:     return getSceneInfo();
        case AgentAction::MoveEntity:       return moveEntity(req.entityId, req.vec);
        case AgentAction::RotateEntity:     return rotateEntity(req.entityId, req.vec);
        case AgentAction::ResizeEntity:     return resizeEntity(req.entityId, req.vec);
        case AgentAction::AddEntity:        return addEntity(req.entityId, req.entityType, req.queryString, req.vec);
        case AgentAction::DeleteEntity:     return deleteEntity(req.entityId);
        case AgentAction::ConnectEntities:  return connectEntities(req.entityId, req.targetId);
        case AgentAction::GetCostDelta:     return getCostDelta();
        case AgentAction::GetScheduleImpact: return getScheduleImpact();
    }
    return {false, "Unknown action", ""};
}

ActionResult AgentBridge::queryByType(const std::string& type) {
    auto entities = m_scene.queryByType(type);
    nlohmann::json arr = nlohmann::json::array();
    for (const auto* e : entities) {
        arr.push_back({{"id", e->id()}, {"name", e->name()}, {"type", e->typeName()}});
    }
    return {true, std::to_string(entities.size()) + " entities found", arr.dump()};
}

ActionResult AgentBridge::queryByName(const std::string& name) {
    auto entities = m_scene.queryByName(name);
    nlohmann::json arr = nlohmann::json::array();
    for (const auto* e : entities) {
        arr.push_back({{"id", e->id()}, {"name", e->name()}, {"type", e->typeName()}});
    }
    return {true, std::to_string(entities.size()) + " entities found", arr.dump()};
}

ActionResult AgentBridge::getPosition(const std::string& id) {
    const auto* e = m_scene.findEntity(id);
    if (!e) return {false, "Entity not found: " + id, ""};
    nlohmann::json j;
    j["id"] = e->id();
    j["position"] = {e->position().x, e->position().y, e->position().z};
    return {true, "OK", j.dump()};
}

ActionResult AgentBridge::getNearby(const std::string& id, double radius) {
    auto entities = m_scene.nearbyEntities(id, radius);
    nlohmann::json arr = nlohmann::json::array();
    for (const auto* e : entities) {
        arr.push_back({{"id", e->id()}, {"name", e->name()}, {"type", e->typeName()}});
    }
    return {true, std::to_string(entities.size()) + " nearby", arr.dump()};
}

ActionResult AgentBridge::getSceneInfo() {
    return {true, "OK", m_scene.sceneInfo()};
}

ActionResult AgentBridge::moveEntity(const std::string& id, const Vec3& pos) {
    if (!m_scene.moveEntity(id, pos)) return {false, "Move failed: " + id, ""};
    return {true, "Moved " + id, ""};
}

ActionResult AgentBridge::rotateEntity(const std::string& id, const Vec3& rot) {
    if (!m_scene.rotateEntity(id, rot)) return {false, "Rotate failed: " + id, ""};
    return {true, "Rotated " + id, ""};
}

ActionResult AgentBridge::resizeEntity(const std::string& id, const Vec3& dims) {
    if (!m_scene.resizeEntity(id, dims)) return {false, "Resize failed: " + id, ""};
    return {true, "Resized " + id, ""};
}

ActionResult AgentBridge::addEntity(const std::string& id, EntityType type, const std::string& name, const Vec3& pos) {
    BIMEntity entity(id, type, name);
    entity.setPosition(pos);
    if (!m_scene.addEntity(entity)) return {false, "Add failed (duplicate?): " + id, ""};
    return {true, "Added " + id, ""};
}

ActionResult AgentBridge::deleteEntity(const std::string& id) {
    if (!m_scene.removeEntity(id)) return {false, "Delete failed: " + id, ""};
    return {true, "Deleted " + id, ""};
}

ActionResult AgentBridge::connectEntities(const std::string& fromId, const std::string& toId) {
    if (!m_scene.connectEntities(fromId, toId)) return {false, "Connect failed", ""};
    return {true, "Connected " + fromId + " <-> " + toId, ""};
}

ActionResult AgentBridge::getCostDelta() {
    double current = m_scene.totalCost();
    double delta = current - m_lastTotalCost;
    m_lastTotalCost = current;
    nlohmann::json j;
    j["previousTotal"] = current - delta;
    j["currentTotal"] = current;
    j["delta"] = delta;
    return {true, "OK", j.dump()};
}

ActionResult AgentBridge::getScheduleImpact() {
    // Simplified: schedule impact based on entity count
    int count = m_scene.entityCount();
    nlohmann::json j;
    j["entityCount"] = count;
    j["estimatedDays"] = count * 0.5;  // Simple heuristic
    j["impact"] = count > 50 ? "high" : (count > 20 ? "medium" : "low");
    return {true, "OK", j.dump()};
}

std::string AgentBridge::executeJson(const std::string& requestJson) {
    try {
        auto j = nlohmann::json::parse(requestJson);
        ActionRequest req;
        std::string actionStr = j.value("action", "");

        // Helper: safely extract Vec3 from JSON array with bounds checking
        auto parseVec3 = [](const nlohmann::json& j, const std::string& key) -> Vec3 {
            if (!j.contains(key) || !j[key].is_array() || j[key].size() < 3)
                throw std::invalid_argument("Missing or invalid Vec3 array: " + key);
            const auto& arr = j[key];
            return {arr[0].get<double>(), arr[1].get<double>(), arr[2].get<double>()};
        };

        if (actionStr == "query_by_type")       { req.action = AgentAction::QueryByType; req.queryString = j.value("type", ""); }
        else if (actionStr == "query_by_name")  { req.action = AgentAction::QueryByName; req.queryString = j.value("name", ""); }
        else if (actionStr == "get_position")   { req.action = AgentAction::GetPosition; req.entityId = j.value("id", ""); }
        else if (actionStr == "get_nearby")     { req.action = AgentAction::GetNearby; req.entityId = j.value("id", ""); req.radius = j.value("radius", 10.0); }
        else if (actionStr == "get_scene_info") { req.action = AgentAction::GetSceneInfo; }
        else if (actionStr == "move")           { req.action = AgentAction::MoveEntity; req.entityId = j.value("id", ""); req.vec = parseVec3(j, "position"); }
        else if (actionStr == "rotate")         { req.action = AgentAction::RotateEntity; req.entityId = j.value("id", ""); req.vec = parseVec3(j, "rotation"); }
        else if (actionStr == "resize")         { req.action = AgentAction::ResizeEntity; req.entityId = j.value("id", ""); req.vec = parseVec3(j, "dimensions"); }
        else if (actionStr == "add")            { req.action = AgentAction::AddEntity; req.entityId = j.value("id", ""); req.entityType = entityTypeFromString(j.value("type", "Generic")); req.queryString = j.value("name", ""); req.vec = parseVec3(j, "position"); }
        else if (actionStr == "delete")         { req.action = AgentAction::DeleteEntity; req.entityId = j.value("id", ""); }
        else if (actionStr == "connect")        { req.action = AgentAction::ConnectEntities; req.entityId = j.value("from", ""); req.targetId = j.value("to", ""); }
        else if (actionStr == "cost_delta")     { req.action = AgentAction::GetCostDelta; }
        else if (actionStr == "schedule_impact"){ req.action = AgentAction::GetScheduleImpact; }
        else { return nlohmann::json({{"success", false}, {"message", "Unknown action: " + actionStr}}).dump(); }

        auto result = execute(req);
        nlohmann::json resp;
        resp["success"] = result.success;
        resp["message"] = result.message;
        if (!result.data.empty()) resp["data"] = nlohmann::json::parse(result.data);
        return resp.dump();
    } catch (const std::exception& ex) {
        return nlohmann::json({{"success", false}, {"message", std::string("Parse error: ") + ex.what()}}).dump();
    }
}

} // namespace bim
