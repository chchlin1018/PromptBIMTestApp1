#pragma once
// BIMSceneGraph.h — Scene graph + node management + query (no Qt)

#include "BIMEntity.h"
#include <unordered_map>
#include <vector>
#include <string>
#include <functional>

namespace bim {

class BIMSceneGraph {
public:
    BIMSceneGraph() = default;

    // Entity management
    bool addEntity(const BIMEntity& entity);
    bool removeEntity(const std::string& id);
    void clear();
    [[nodiscard]] int entityCount() const noexcept { return static_cast<int>(m_entities.size()); }

    // Lookup
    [[nodiscard]] BIMEntity* findEntity(const std::string& id);
    [[nodiscard]] const BIMEntity* findEntity(const std::string& id) const;
    [[nodiscard]] bool hasEntity(const std::string& id) const;

    // Query
    [[nodiscard]] std::vector<const BIMEntity*> queryByType(EntityType type) const;
    [[nodiscard]] std::vector<const BIMEntity*> queryByType(const std::string& typeName) const;
    [[nodiscard]] std::vector<const BIMEntity*> queryByName(const std::string& nameSubstr) const;
    [[nodiscard]] std::vector<const BIMEntity*> nearbyEntities(const std::string& id, double radius) const;
    [[nodiscard]] std::vector<const BIMEntity*> allEntities() const;

    // Operations
    bool moveEntity(const std::string& id, const Vec3& position);
    bool rotateEntity(const std::string& id, const Vec3& rotation);
    bool resizeEntity(const std::string& id, const Vec3& dimensions);
    bool connectEntities(const std::string& fromId, const std::string& toId);

    // Cost
    [[nodiscard]] double totalCost() const;
    [[nodiscard]] double pipeCost(const std::string& fromId, const std::string& toId, double costPerMeter = 3500.0) const;

    // Serialization
    [[nodiscard]] std::string toJson() const;
    [[nodiscard]] static BIMSceneGraph fromJson(const std::string& json);
    [[nodiscard]] std::string sceneInfo() const;

private:
    std::unordered_map<std::string, BIMEntity> m_entities;
};

} // namespace bim
