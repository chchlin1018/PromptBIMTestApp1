#pragma once
// PropertyManager.h — BIM property management (material/cost/dimensions)

#include "BIMTypes.h"
#include <string>
#include <map>
#include <vector>
#include <optional>

namespace bim {

struct MaterialSpec {
    std::string name;
    std::string category;  // structural, finish, insulation, etc.
    double density = 0.0;  // kg/m3
    double costPerUnit = 0.0;  // NT$/m3 or NT$/m2
    std::string unit;  // m3, m2, each
};

struct PropertyTemplate {
    EntityType entityType;
    std::map<std::string, std::string> defaultProperties;
};

class PropertyManager {
public:
    PropertyManager();

    // Material management
    void registerMaterial(const std::string& id, const MaterialSpec& spec);
    std::optional<MaterialSpec> getMaterial(const std::string& id) const;
    std::vector<std::string> getMaterialsByCategory(const std::string& category) const;

    // Property templates for entity types
    void registerTemplate(EntityType type, const std::map<std::string, std::string>& defaults);
    std::map<std::string, std::string> getDefaultProperties(EntityType type) const;

    // Property validation
    static bool isValidProperty(const std::string& key, const std::string& value);
    static double parseNumericProperty(const std::string& value, double defaultVal = 0.0);

    // Cost lookup for material
    double materialCost(const std::string& materialId, double quantity) const;

    // Built-in material count
    int materialCount() const { return static_cast<int>(m_materials.size()); }

    // Serialization
    std::string toJson() const;

private:
    void registerBuiltinMaterials();
    void registerBuiltinTemplates();

    std::map<std::string, MaterialSpec> m_materials;
    std::map<EntityType, PropertyTemplate> m_templates;
};

} // namespace bim
