#pragma once
/// @file AgentBridge.h
/// @brief AI Agent action bridge — maps 13 agent actions to BIMSceneGraph operations.
///
/// Pure logic layer (no Qt, no IPC). Receives structured ActionRequest or raw JSON
/// from the Python AI layer and dispatches to the appropriate scene graph operation.

#include "BIMSceneGraph.h"
#include <string>
#include <functional>

namespace bim {

/// All 13 supported agent actions matching Python IntentRouter ACTION_MAP.
enum class AgentAction {
    QueryByType, QueryByName, GetPosition, GetNearby, GetSceneInfo,
    MoveEntity, RotateEntity, ResizeEntity, AddEntity, DeleteEntity,
    ConnectEntities, GetCostDelta, GetScheduleImpact
};

constexpr int AGENT_ACTION_COUNT = 13;

/// @brief Structured request for a single agent action.
struct ActionRequest {
    AgentAction action;            ///< The action to perform
    std::string entityId;          ///< Target entity ID (e.g. "chiller-1")
    std::string targetId;          ///< Secondary entity ID (for connect)
    std::string queryString;       ///< Query string (type name or search term)
    Vec3 vec;                      ///< Position/rotation/dimensions vector
    EntityType entityType = EntityType::Generic; ///< Entity type for add action
    std::map<std::string, std::string> properties; ///< Optional properties
    double radius = 10.0;          ///< Search radius for get_nearby (meters)
};

/// @brief Result of an agent action execution.
struct ActionResult {
    bool success = false;          ///< Whether the action succeeded
    std::string message;           ///< Human-readable result message
    std::string data;              ///< JSON payload with detailed results
};

/// @brief AI Agent bridge — translates parsed intents into scene graph operations.
///
/// Used by the Python AI layer (via pybind11) to execute BIM operations.
/// Supports all 13 AgentBridge actions: 5 query + 5 mutation + connect + cost + schedule.
class AgentBridge {
public:
    /// @brief Construct an AgentBridge bound to a scene graph.
    /// @param scene Reference to the BIMSceneGraph to operate on
    explicit AgentBridge(BIMSceneGraph& scene);

    /// @brief Execute a structured action request via dispatch.
    /// @param req The action request containing action type and parameters
    /// @return ActionResult with success status, message, and optional JSON data
    [[nodiscard]] ActionResult execute(const ActionRequest& req);

    /// @brief Query all entities of a given type (e.g. "Wall", "Chiller").
    /// @param type Entity type name string matching EntityType enum
    /// @return JSON array of matching entities with id/name/type
    [[nodiscard]] ActionResult queryByType(const std::string& type);

    /// @brief Query entities by name substring match.
    /// @param name Search string to match against entity names
    /// @return JSON array of matching entities
    [[nodiscard]] ActionResult queryByName(const std::string& name);

    /// @brief Get the 3D position of an entity.
    /// @param id Entity ID (e.g. "chiller-1")
    /// @return JSON with id and position [x, y, z]
    [[nodiscard]] ActionResult getPosition(const std::string& id);

    /// @brief Find entities within a radius of the specified entity.
    /// @param id Center entity ID
    /// @param radius Search radius in meters
    /// @return JSON array of nearby entities
    [[nodiscard]] ActionResult getNearby(const std::string& id, double radius);

    /// @brief Get overall scene information (entity count, types, bounds).
    /// @return JSON scene summary
    [[nodiscard]] ActionResult getSceneInfo();

    /// @brief Move an entity to a new position.
    /// @param id Entity ID to move
    /// @param pos New position vector (x, y, z)
    /// @return Success/failure with message
    [[nodiscard]] ActionResult moveEntity(const std::string& id, const Vec3& pos);

    /// @brief Rotate an entity by the given angles.
    /// @param id Entity ID to rotate
    /// @param rot Rotation vector (rx, ry, rz) in degrees
    /// @return Success/failure with message
    [[nodiscard]] ActionResult rotateEntity(const std::string& id, const Vec3& rot);

    /// @brief Resize an entity to new dimensions.
    /// @param id Entity ID to resize
    /// @param dims New dimensions (width, height, depth)
    /// @return Success/failure with message
    [[nodiscard]] ActionResult resizeEntity(const std::string& id, const Vec3& dims);

    /// @brief Add a new entity to the scene.
    /// @param id Unique entity ID
    /// @param type Entity type enum value
    /// @param name Human-readable name
    /// @param pos Initial position vector
    /// @return Success/failure (fails if ID already exists)
    [[nodiscard]] ActionResult addEntity(const std::string& id, EntityType type, const std::string& name, const Vec3& pos);

    /// @brief Remove an entity from the scene.
    /// @param id Entity ID to delete
    /// @return Success/failure with message
    [[nodiscard]] ActionResult deleteEntity(const std::string& id);

    /// @brief Create a bidirectional connection between two entities.
    /// @param fromId Source entity ID
    /// @param toId Target entity ID
    /// @return Success/failure with message
    [[nodiscard]] ActionResult connectEntities(const std::string& fromId, const std::string& toId);

    /// @brief Calculate cost change since last call (NT$ delta).
    /// @return JSON with previousTotal, currentTotal, delta
    [[nodiscard]] ActionResult getCostDelta();

    /// @brief Estimate schedule impact based on entity count.
    /// @return JSON with entityCount, estimatedDays, impact level
    [[nodiscard]] ActionResult getScheduleImpact();

    /// @brief Parse a JSON action string, execute, and return JSON response.
    /// @param requestJson JSON string with "action" and parameters
    /// @return JSON response string with success, message, and optional data
    [[nodiscard]] std::string executeJson(const std::string& requestJson);

private:
    BIMSceneGraph& m_scene;
    double m_lastTotalCost = 0.0;
};

} // namespace bim
