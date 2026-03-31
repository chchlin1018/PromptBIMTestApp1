#include "BIMEntity.h"
#include <nlohmann/json.hpp>
#include <cmath>
#include <algorithm>

namespace bim {

BIMEntity::BIMEntity(const std::string& id, EntityType type, const std::string& name)
    : m_id(id), m_type(type), m_typeName(entityTypeName(type)), m_name(name) {}

void BIMEntity::setType(EntityType type) {
    m_type = type;
    m_typeName = entityTypeName(type);
}

void BIMEntity::setProperty(const std::string& key, const std::string& value) {
    m_properties[key] = value;
}

std::string BIMEntity::getProperty(const std::string& key, const std::string& defaultVal) const {
    auto it = m_properties.find(key);
    return it != m_properties.end() ? it->second : defaultVal;
}

bool BIMEntity::hasProperty(const std::string& key) const {
    return m_properties.count(key) > 0;
}

void BIMEntity::removeProperty(const std::string& key) {
    m_properties.erase(key);
}

void BIMEntity::addConnection(const std::string& targetId) {
    if (!isConnectedTo(targetId)) {
        m_connections.push_back(targetId);
    }
}

void BIMEntity::removeConnection(const std::string& targetId) {
    m_connections.erase(
        std::remove(m_connections.begin(), m_connections.end(), targetId),
        m_connections.end()
    );
}

bool BIMEntity::isConnectedTo(const std::string& targetId) const {
    return std::find(m_connections.begin(), m_connections.end(), targetId) != m_connections.end();
}

double BIMEntity::distanceTo(const BIMEntity& other) const {
    return m_position.distanceTo(other.m_position);
}

double BIMEntity::volume() const {
    return std::abs(m_dimensions.x * m_dimensions.y * m_dimensions.z);
}

double BIMEntity::surfaceArea() const {
    double w = std::abs(m_dimensions.x);
    double h = std::abs(m_dimensions.y);
    double d = std::abs(m_dimensions.z);
    return 2.0 * (w * h + h * d + w * d);
}

std::string BIMEntity::toJson() const {
    nlohmann::json j;
    j["id"] = m_id;
    j["type"] = m_typeName;
    j["name"] = m_name;
    j["position"] = {m_position.x, m_position.y, m_position.z};
    j["rotation"] = {m_rotation.x, m_rotation.y, m_rotation.z};
    j["dimensions"] = {m_dimensions.x, m_dimensions.y, m_dimensions.z};

    nlohmann::json props = nlohmann::json::object();
    for (const auto& [k, v] : m_properties) props[k] = v;
    j["properties"] = props;
    j["connections"] = m_connections;
    return j.dump();
}

BIMEntity BIMEntity::fromJson(const std::string& json) {
    auto j = nlohmann::json::parse(json);
    BIMEntity e;
    e.m_id = j.value("id", "");
    std::string typeStr = j.value("type", "Generic");
    e.m_type = entityTypeFromString(typeStr);
    e.m_typeName = typeStr;
    e.m_name = j.value("name", "");

    if (j.contains("position") && j["position"].is_array() && j["position"].size() >= 3) {
        e.m_position = {j["position"][0], j["position"][1], j["position"][2]};
    }
    if (j.contains("rotation") && j["rotation"].is_array() && j["rotation"].size() >= 3) {
        e.m_rotation = {j["rotation"][0], j["rotation"][1], j["rotation"][2]};
    }
    if (j.contains("dimensions") && j["dimensions"].is_array() && j["dimensions"].size() >= 3) {
        e.m_dimensions = {j["dimensions"][0], j["dimensions"][1], j["dimensions"][2]};
    }
    if (j.contains("properties") && j["properties"].is_object()) {
        for (auto& [k, v] : j["properties"].items()) {
            e.m_properties[k] = v.get<std::string>();
        }
    }
    if (j.contains("connections") && j["connections"].is_array()) {
        for (const auto& c : j["connections"]) {
            e.m_connections.push_back(c.get<std::string>());
        }
    }
    return e;
}

} // namespace bim
