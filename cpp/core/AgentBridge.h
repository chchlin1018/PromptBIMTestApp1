#pragma once
// AgentBridge.h — AI Agent action bridge (no Qt, no IPC — pure logic)
// Maps 13 agent actions to scene graph operations

#include "BIMSceneGraph.h"
#include <string>
#include <functional>

namespace bim {

enum class AgentAction {
    QueryByType, QueryByName, GetPosition, GetNearby, GetSceneInfo,
    MoveEntity, RotateEntity, ResizeEntity, AddEntity, DeleteEntity,
    ConnectEntities, GetCostDelta, GetScheduleImpact
};

constexpr int AGENT_ACTION_COUNT = 13;

struct ActionRequest {
    AgentAction action;
    std::string entityId;
    std::string targetId;
    std::string queryString;
    Vec3 vec;
    EntityType entityType = EntityType::Generic;
    std::map<std::string, std::string> properties;
    double radius = 10.0;
};

struct ActionResult {
    bool success = false;
    std::string message;
    std::string data; // JSON
};

class AgentBridge {
public:
    explicit AgentBridge(BIMSceneGraph& scene);

    // Execute an action request
    [[nodiscard]] ActionResult execute(const ActionRequest& req);

    // Convenience methods for all 13 actions
    [[nodiscard]] ActionResult queryByType(const std::string& type);
    [[nodiscard]] ActionResult queryByName(const std::string& name);
    [[nodiscard]] ActionResult getPosition(const std::string& id);
    [[nodiscard]] ActionResult getNearby(const std::string& id, double radius);
    [[nodiscard]] ActionResult getSceneInfo();

    ActionResult moveEntity(const std::string& id, const Vec3& pos);
    ActionResult rotateEntity(const std::string& id, const Vec3& rot);
    ActionResult resizeEntity(const std::string& id, const Vec3& dims);
    ActionResult addEntity(const std::string& id, EntityType type, const std::string& name, const Vec3& pos);
    ActionResult deleteEntity(const std::string& id);
    ActionResult connectEntities(const std::string& fromId, const std::string& toId);

    [[nodiscard]] ActionResult getCostDelta();
    [[nodiscard]] ActionResult getScheduleImpact();

    // Parse action from JSON string, execute, return JSON
    [[nodiscard]] std::string executeJson(const std::string& requestJson);

private:
    BIMSceneGraph& m_scene;
    double m_lastTotalCost = 0.0;
};

} // namespace bim
