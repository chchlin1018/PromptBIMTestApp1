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
    const std::string& id() const { return m_id; }
    EntityType type() const { return m_type; }
    const std::string& typeName() const { return m_typeName; }
    const std::string& name() const { return m_name; }
    const Vec3& position() const { return m_position; }
    const Vec3& rotation() const { return m_rotation; }
    const Vec3& dimensions() const { return m_dimensions; }
    const std::map<std::string, std::string>& properties() const { return m_properties; }
    const std::vector<std::string>& connections() const { return m_connections; }

    // Mutators
    void setId(const std::string& id) { m_id = id; }
    void setType(EntityType type);
    void setName(const std::string& name) { m_name = name; }
    void setPosition(const Vec3& pos) { m_position = pos; }
    void setRotation(const Vec3& rot) { m_rotation = rot; }
    void setDimensions(const Vec3& dims) { m_dimensions = dims; }

    // Properties
    void setProperty(const std::string& key, const std::string& value);
    std::string getProperty(const std::string& key, const std::string& defaultVal = "") const;
    bool hasProperty(const std::string& key) const;
    void removeProperty(const std::string& key);

    // Connections
    void addConnection(const std::string& targetId);
    void removeConnection(const std::string& targetId);
    bool isConnectedTo(const std::string& targetId) const;

    // Geometry
    double distanceTo(const BIMEntity& other) const;
    double volume() const;
    double surfaceArea() const;

    // Serialization (JSON string)
    std::string toJson() const;
    static BIMEntity fromJson(const std::string& json);

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
