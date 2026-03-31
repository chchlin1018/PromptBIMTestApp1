#include "PropertyManager.h"
#include <nlohmann/json.hpp>
#include <stdexcept>

namespace bim {

PropertyManager::PropertyManager() {
    registerBuiltinMaterials();
    registerBuiltinTemplates();
}

void PropertyManager::registerBuiltinMaterials() {
    m_materials["concrete_rc"] = {"RC Concrete", "structural", 2400.0, 8500.0, "m3"};
    m_materials["steel_structural"] = {"Structural Steel", "structural", 7850.0, 45000.0, "ton"};
    m_materials["rebar"] = {"Rebar", "structural", 7850.0, 32000.0, "ton"};
    m_materials["brick"] = {"Brick", "finish", 1800.0, 3500.0, "m2"};
    m_materials["glass_curtain"] = {"Curtain Wall Glass", "finish", 2500.0, 12000.0, "m2"};
    m_materials["gypsum_board"] = {"Gypsum Board", "finish", 800.0, 650.0, "m2"};
    m_materials["tile_floor"] = {"Floor Tile", "finish", 2100.0, 1800.0, "m2"};
    m_materials["insulation_xps"] = {"XPS Insulation", "insulation", 35.0, 900.0, "m2"};
    m_materials["copper_pipe"] = {"Copper Pipe", "mep", 8900.0, 3500.0, "m"};
    m_materials["pvc_pipe"] = {"PVC Pipe", "mep", 1400.0, 450.0, "m"};
    m_materials["steel_duct"] = {"Steel Duct", "mep", 7850.0, 2800.0, "m2"};
    m_materials["cable_power"] = {"Power Cable", "mep", 0.0, 850.0, "m"};
}

void PropertyManager::registerBuiltinTemplates() {
    m_templates[EntityType::Wall] = {EntityType::Wall, {
        {"material", "concrete_rc"}, {"thickness", "0.2"}, {"height", "3.0"}, {"fire_rating", "2h"}}};
    m_templates[EntityType::Column] = {EntityType::Column, {
        {"material", "concrete_rc"}, {"cross_section", "0.6x0.6"}, {"height", "3.6"}}};
    m_templates[EntityType::Slab] = {EntityType::Slab, {
        {"material", "concrete_rc"}, {"thickness", "0.15"}, {"finish", "tile_floor"}}};
    m_templates[EntityType::Beam] = {EntityType::Beam, {
        {"material", "concrete_rc"}, {"depth", "0.6"}, {"width", "0.3"}}};
    m_templates[EntityType::Chiller] = {EntityType::Chiller, {
        {"capacity_kw", "500"}, {"power_kw", "150"}, {"refrigerant", "R-134a"}, {"cost", "2500000"}}};
    m_templates[EntityType::CoolingTower] = {EntityType::CoolingTower, {
        {"capacity_kw", "600"}, {"power_kw", "15"}, {"cost", "800000"}}};
    m_templates[EntityType::Pump] = {EntityType::Pump, {
        {"flow_lps", "50"}, {"head_m", "30"}, {"power_kw", "15"}, {"cost", "180000"}}};
    m_templates[EntityType::Pipe] = {EntityType::Pipe, {
        {"material", "copper_pipe"}, {"diameter_mm", "100"}, {"cost_per_m", "3500"}}};
}

void PropertyManager::registerMaterial(const std::string& id, const MaterialSpec& spec) {
    m_materials[id] = spec;
}

std::optional<MaterialSpec> PropertyManager::getMaterial(const std::string& id) const {
    auto it = m_materials.find(id);
    if (it != m_materials.end()) return it->second;
    return std::nullopt;
}

std::vector<std::string> PropertyManager::getMaterialsByCategory(const std::string& category) const {
    std::vector<std::string> result;
    for (const auto& [id, spec] : m_materials) {
        if (spec.category == category) result.push_back(id);
    }
    return result;
}

void PropertyManager::registerTemplate(EntityType type, const std::map<std::string, std::string>& defaults) {
    m_templates[type] = {type, defaults};
}

std::map<std::string, std::string> PropertyManager::getDefaultProperties(EntityType type) const {
    auto it = m_templates.find(type);
    if (it != m_templates.end()) return it->second.defaultProperties;
    return {};
}

bool PropertyManager::isValidProperty(const std::string& key, const std::string& value) {
    return !key.empty() && !value.empty();
}

double PropertyManager::parseNumericProperty(const std::string& value, double defaultVal) {
    try { return std::stod(value); } catch (...) { return defaultVal; }
}

double PropertyManager::materialCost(const std::string& materialId, double quantity) const {
    auto mat = getMaterial(materialId);
    if (!mat) return 0.0;
    return mat->costPerUnit * quantity;
}

std::string PropertyManager::toJson() const {
    nlohmann::json j;
    nlohmann::json mats = nlohmann::json::object();
    for (const auto& [id, spec] : m_materials) {
        mats[id] = {{"name", spec.name}, {"category", spec.category},
                     {"density", spec.density}, {"costPerUnit", spec.costPerUnit}, {"unit", spec.unit}};
    }
    j["materials"] = mats;
    j["materialCount"] = materialCount();
    return j.dump();
}

} // namespace bim
