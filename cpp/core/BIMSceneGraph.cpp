#include "BIMSceneGraph.h"
#include <nlohmann/json.hpp>
#include <algorithm>

namespace bim {

bool BIMSceneGraph::addEntity(const BIMEntity& entity) {
    if (entity.id().empty() || m_entities.count(entity.id())) return false;
    m_entities.emplace(entity.id(), entity);
    return true;
}

bool BIMSceneGraph::removeEntity(const std::string& id) {
    return m_entities.erase(id) > 0;
}

void BIMSceneGraph::clear() {
    m_entities.clear();
}

BIMEntity* BIMSceneGraph::findEntity(const std::string& id) {
    auto it = m_entities.find(id);
    return it != m_entities.end() ? &it->second : nullptr;
}

const BIMEntity* BIMSceneGraph::findEntity(const std::string& id) const {
    auto it = m_entities.find(id);
    return it != m_entities.end() ? &it->second : nullptr;
}

bool BIMSceneGraph::hasEntity(const std::string& id) const {
    return m_entities.count(id) > 0;
}

std::vector<const BIMEntity*> BIMSceneGraph::queryByType(EntityType type) const {
    std::vector<const BIMEntity*> result;
    result.reserve(m_entities.size() / 4); // Heuristic: ~25% match rate
    for (const auto& [_, e] : m_entities) {
        if (e.type() == type) result.push_back(&e);
    }
    return result;
}

std::vector<const BIMEntity*> BIMSceneGraph::queryByType(const std::string& typeName) const {
    return queryByType(entityTypeFromString(typeName));
}

std::vector<const BIMEntity*> BIMSceneGraph::queryByName(const std::string& nameSubstr) const {
    std::vector<const BIMEntity*> result;
    for (const auto& [_, e] : m_entities) {
        if (e.name().find(nameSubstr) != std::string::npos) result.push_back(&e);
    }
    return result;
}

std::vector<const BIMEntity*> BIMSceneGraph::nearbyEntities(const std::string& id, double radius) const {
    std::vector<const BIMEntity*> result;
    auto it = m_entities.find(id);
    if (it == m_entities.end()) return result;
    const auto& center = it->second.position();
    for (const auto& [eid, e] : m_entities) {
        if (eid == id) continue;
        if (e.position().distanceTo(center) <= radius) result.push_back(&e);
    }
    return result;
}

std::vector<const BIMEntity*> BIMSceneGraph::allEntities() const {
    std::vector<const BIMEntity*> result;
    result.reserve(m_entities.size());
    for (const auto& [_, e] : m_entities) result.push_back(&e);
    return result;
}

bool BIMSceneGraph::moveEntity(const std::string& id, const Vec3& position) {
    auto* e = findEntity(id);
    if (!e) return false;
    e->setPosition(position);
    return true;
}

bool BIMSceneGraph::rotateEntity(const std::string& id, const Vec3& rotation) {
    auto* e = findEntity(id);
    if (!e) return false;
    e->setRotation(rotation);
    return true;
}

bool BIMSceneGraph::resizeEntity(const std::string& id, const Vec3& dimensions) {
    auto* e = findEntity(id);
    if (!e) return false;
    e->setDimensions(dimensions);
    return true;
}

bool BIMSceneGraph::connectEntities(const std::string& fromId, const std::string& toId) {
    auto* from = findEntity(fromId);
    auto* to = findEntity(toId);
    if (!from || !to) return false;
    from->addConnection(toId);
    to->addConnection(fromId);
    return true;
}

double BIMSceneGraph::totalCost() const {
    double total = 0.0;
    for (const auto& [_, e] : m_entities) {
        std::string costStr = e.getProperty("cost", "0");
        try { total += std::stod(costStr); } catch (...) {}
    }
    return total;
}

double BIMSceneGraph::pipeCost(const std::string& fromId, const std::string& toId, double costPerMeter) const {
    const auto* from = findEntity(fromId);
    const auto* to = findEntity(toId);
    if (!from || !to) return 0.0;
    return from->distanceTo(*to) * costPerMeter;
}

std::string BIMSceneGraph::toJson() const {
    nlohmann::json j = nlohmann::json::object();
    nlohmann::json entities = nlohmann::json::array();
    for (const auto& [_, e] : m_entities) {
        entities.push_back(nlohmann::json::parse(e.toJson()));
    }
    j["entities"] = entities;
    j["entityCount"] = entityCount();
    return j.dump();
}

BIMSceneGraph BIMSceneGraph::fromJson(const std::string& json) {
    BIMSceneGraph sg;
    auto j = nlohmann::json::parse(json);
    if (j.contains("entities") && j["entities"].is_array()) {
        for (const auto& ej : j["entities"]) {
            sg.addEntity(BIMEntity::fromJson(ej.dump()));
        }
    }
    return sg;
}

std::string BIMSceneGraph::sceneInfo() const {
    nlohmann::json info;
    info["entityCount"] = entityCount();
    info["totalCost"] = totalCost();

    std::map<std::string, int> typeCounts;
    for (const auto& [_, e] : m_entities) {
        typeCounts[e.typeName()]++;
    }
    info["typeDistribution"] = typeCounts;
    return info.dump();
}

} // namespace bim
