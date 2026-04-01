#pragma once
/// @file BIMEntity.h
/// @brief Standalone BIM entity — core data model for all 22 entity types.
/// No Qt dependency. Supports spatial queries, properties, connections, and JSON serialization.

#include "BIMTypes.h"
#include <string>
#include <map>
#include <vector>

namespace bim {

/// @brief A single BIM entity with type, position, dimensions, properties, and connections.
///
/// Represents any of the 22 EntityType values. Used by BIMSceneGraph for spatial management
/// and by AgentBridge for AI-driven operations.
class BIMEntity {
public:
    BIMEntity() = default;

    /// @brief Construct a BIMEntity with ID, type, and name.
    /// @param id Unique identifier (e.g. "chiller-1", "wall-2")
    /// @param type One of 22 EntityType enum values
    /// @param name Human-readable display name
    BIMEntity(const std::string& id, EntityType type, const std::string& name);

    // --- Accessors ---
    [[nodiscard]] const std::string& id() const noexcept { return m_id; }          ///< Unique entity ID
    [[nodiscard]] EntityType type() const noexcept { return m_type; }               ///< Entity type enum
    [[nodiscard]] const std::string& typeName() const noexcept { return m_typeName; } ///< Type as string
    [[nodiscard]] const std::string& name() const noexcept { return m_name; }       ///< Display name
    [[nodiscard]] const Vec3& position() const noexcept { return m_position; }      ///< 3D position (meters)
    [[nodiscard]] const Vec3& rotation() const noexcept { return m_rotation; }      ///< Euler rotation (degrees)
    [[nodiscard]] const Vec3& dimensions() const noexcept { return m_dimensions; }  ///< Bounding box (w, h, d)
    [[nodiscard]] const std::map<std::string, std::string>& properties() const noexcept { return m_properties; } ///< Key-value property map
    [[nodiscard]] const std::vector<std::string>& connections() const noexcept { return m_connections; } ///< Connected entity IDs

    // --- Mutators ---
    void setId(const std::string& id) { m_id = id; }                     ///< Set entity ID
    void setType(EntityType type);                                        ///< Set type (updates typeName)
    void setName(const std::string& name) { m_name = name; }             ///< Set display name
    void setPosition(const Vec3& pos) noexcept { m_position = pos; }     ///< Set 3D position
    void setRotation(const Vec3& rot) noexcept { m_rotation = rot; }     ///< Set rotation angles
    void setDimensions(const Vec3& dims) noexcept { m_dimensions = dims; } ///< Set bounding dimensions

    // --- Properties (key-value metadata) ---
    /// @brief Set a custom property (e.g. "material", "manufacturer").
    void setProperty(const std::string& key, const std::string& value);
    /// @brief Get a property value, or defaultVal if not found.
    [[nodiscard]] std::string getProperty(const std::string& key, const std::string& defaultVal = "") const;
    /// @brief Check if a property key exists.
    [[nodiscard]] bool hasProperty(const std::string& key) const;
    /// @brief Remove a property by key.
    void removeProperty(const std::string& key);

    // --- Connections (bidirectional entity links) ---
    /// @brief Add a connection to another entity by ID.
    void addConnection(const std::string& targetId);
    /// @brief Remove a connection to another entity.
    void removeConnection(const std::string& targetId);
    /// @brief Check if this entity is connected to the given target.
    [[nodiscard]] bool isConnectedTo(const std::string& targetId) const;

    // --- Geometry ---
    /// @brief Euclidean distance to another entity (meters).
    [[nodiscard]] double distanceTo(const BIMEntity& other) const;
    /// @brief Volume of the bounding box (w * h * d).
    [[nodiscard]] double volume() const;
    /// @brief Surface area of the bounding box.
    [[nodiscard]] double surfaceArea() const;

    // --- Serialization ---
    /// @brief Serialize entity to JSON string.
    [[nodiscard]] std::string toJson() const;
    /// @brief Deserialize entity from JSON string.
    [[nodiscard]] static BIMEntity fromJson(const std::string& json);

private:
    std::string m_id;
    EntityType m_type = EntityType::Generic;
    std::string m_typeName = "Generic";
    std::string m_name;
    Vec3 m_position;                   ///< World position in meters
    Vec3 m_rotation;                   ///< Euler angles in degrees
    Vec3 m_dimensions{1.0, 1.0, 1.0};  ///< Bounding box (width, height, depth)
    std::map<std::string, std::string> m_properties;  ///< Custom metadata
    std::vector<std::string> m_connections;            ///< Connected entity IDs
};

} // namespace bim
