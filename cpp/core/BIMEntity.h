#pragma once
// BIMEntity.h — Standalone BIM entity (no Qt dependency)

#include "BIMTypes.h"
#include <string>
#include <map>
#include <vector>

namespace bim {

class BIMEntity {
public:
    BIMEntity() = default;
    BIMEntity(const std::string& id, EntityType type, const std::string& name);

    // Accessors
    [[nodiscard]] const std::string& id() const noexcept { return m_id; }
    [[nodiscard]] EntityType type() const noexcept { return m_type; }
    [[nodiscard]] const std::string& typeName() const noexcept { return m_typeName; }
    [[nodiscard]] const std::string& name() const noexcept { return m_name; }
    [[nodiscard]] const Vec3& position() const noexcept { return m_position; }
    [[nodiscard]] const Vec3& rotation() const noexcept { return m_rotation; }
    [[nodiscard]] const Vec3& dimensions() const noexcept { return m_dimensions; }
    [[nodiscard]] const std::map<std::string, std::string>& properties() const noexcept { return m_properties; }
    [[nodiscard]] const std::vector<std::string>& connections() const noexcept { return m_connections; }

    // Mutators
    void setId(const std::string& id) { m_id = id; }
    void setType(EntityType type);
    void setName(const std::string& name) { m_name = name; }
    void setPosition(const Vec3& pos) noexcept { m_position = pos; }
    void setRotation(const Vec3& rot) noexcept { m_rotation = rot; }
    void setDimensions(const Vec3& dims) noexcept { m_dimensions = dims; }

    // Properties
    void setProperty(const std::string& key, const std::string& value);
    [[nodiscard]] std::string getProperty(const std::string& key, const std::string& defaultVal = "") const;
    [[nodiscard]] bool hasProperty(const std::string& key) const;
    void removeProperty(const std::string& key);

    // Connections
    void addConnection(const std::string& targetId);
    void removeConnection(const std::string& targetId);
    [[nodiscard]] bool isConnectedTo(const std::string& targetId) const;

    // Geometry
    [[nodiscard]] double distanceTo(const BIMEntity& other) const;
    [[nodiscard]] double volume() const;
    [[nodiscard]] double surfaceArea() const;

    // Serialization (JSON string)
    [[nodiscard]] std::string toJson() const;
    [[nodiscard]] static BIMEntity fromJson(const std::string& json);

private:
    std::string m_id;
    EntityType m_type = EntityType::Generic;
    std::string m_typeName = "Generic";
    std::string m_name;
    Vec3 m_position;
    Vec3 m_rotation;
    Vec3 m_dimensions{1.0, 1.0, 1.0};
    std::map<std::string, std::string> m_properties;
    std::vector<std::string> m_connections;
};

} // namespace bim
