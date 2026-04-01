#include "CostCalculator.h"
#include <nlohmann/json.hpp>
#include <cmath>

namespace bim {

CostCalculator::CostCalculator(const PropertyManager& props) : m_props(props) {}

std::string CostCalculator::categorize(EntityType type) const noexcept {
    switch (type) {
        case EntityType::Wall: case EntityType::Column: case EntityType::Beam:
        case EntityType::Slab: case EntityType::Roof:
            return "structural";
        case EntityType::Chiller: case EntityType::CoolingTower: case EntityType::AHU:
        case EntityType::Pump: case EntityType::Fan: case EntityType::Pipe:
        case EntityType::Duct: case EntityType::Cable: case EntityType::Valve:
        case EntityType::Sensor: case EntityType::ExhaustStack:
            return "mep";
        case EntityType::Door: case EntityType::Window: case EntityType::Stair:
        case EntityType::Elevator: case EntityType::Ramp:
            return "finish";
        default:
            return "other";
    }
}

double CostCalculator::lookupUnitPrice(const BIMEntity& entity) const {
    // Check entity's own cost property first
    std::string costStr = entity.getProperty("cost", "");
    if (!costStr.empty()) {
        try { return std::stod(costStr); } catch (const std::exception&) {}
    }

    // Lookup material cost
    std::string matId = entity.getProperty("material", "");
    if (!matId.empty()) {
        auto mat = m_props.getMaterial(matId);
        if (mat) return mat->costPerUnit;
    }

    // Default costs by entity type (NT$)
    switch (entity.type()) {
        case EntityType::Wall:     return 8500.0;   // per m3
        case EntityType::Column:   return 12000.0;
        case EntityType::Beam:     return 10000.0;
        case EntityType::Slab:     return 6500.0;
        case EntityType::Roof:     return 7500.0;
        case EntityType::Door:     return 25000.0;  // each
        case EntityType::Window:   return 18000.0;
        case EntityType::Chiller:  return 2500000.0;
        case EntityType::CoolingTower: return 800000.0;
        case EntityType::AHU:      return 450000.0;
        case EntityType::Pump:     return 180000.0;
        case EntityType::Pipe:     return 3500.0;   // per m
        case EntityType::Duct:     return 2800.0;
        default:                   return 10000.0;
    }
}

CostItem CostCalculator::calculateEntityCost(const BIMEntity& entity) const {
    CostItem item;
    item.entityId = entity.id();
    item.category = categorize(entity.type());
    item.description = entity.typeName() + ": " + entity.name();
    item.unitPrice = lookupUnitPrice(entity);

    // Quantity: volume for structural, 1 for equipment, length for pipes
    switch (entity.type()) {
        case EntityType::Wall: case EntityType::Column: case EntityType::Beam:
        case EntityType::Slab: case EntityType::Roof:
            item.quantity = entity.volume();
            item.unit = "m3";
            break;
        case EntityType::Pipe: case EntityType::Duct: case EntityType::Cable:
            item.quantity = entity.dimensions().x;  // length
            item.unit = "m";
            break;
        default:
            item.quantity = 1.0;
            item.unit = "each";
            break;
    }

    item.total = item.unitPrice * item.quantity;
    return item;
}

std::vector<CostItem> CostCalculator::calculateAll(const std::vector<const BIMEntity*>& entities) const {
    std::vector<CostItem> items;
    items.reserve(entities.size());
    for (const auto* e : entities) {
        if (!e) continue;
        items.push_back(calculateEntityCost(*e));
    }
    return items;
}

CostSummary CostCalculator::summarize(const std::vector<CostItem>& items, double totalFloorArea) const {
    CostSummary s;
    s.itemCount = static_cast<int>(items.size());
    for (const auto& item : items) {
        if (item.category == "structural") s.structuralCost += item.total;
        else if (item.category == "mep") s.mepCost += item.total;
        else if (item.category == "finish") s.finishCost += item.total;
        else s.otherCost += item.total;
    }
    s.totalCost = s.structuralCost + s.mepCost + s.finishCost + s.otherCost;
    s.costPerSqm = totalFloorArea > 0 ? s.totalCost / totalFloorArea : 0.0;
    return s;
}

double CostCalculator::pipeCost(const BIMEntity& from, const BIMEntity& to, double costPerMeter) const {
    return from.distanceTo(to) * costPerMeter;
}

CostSummary CostCalculator::costDelta(const CostSummary& before, const CostSummary& after) const {
    CostSummary delta;
    delta.structuralCost = after.structuralCost - before.structuralCost;
    delta.mepCost = after.mepCost - before.mepCost;
    delta.finishCost = after.finishCost - before.finishCost;
    delta.otherCost = after.otherCost - before.otherCost;
    delta.totalCost = after.totalCost - before.totalCost;
    delta.costPerSqm = after.costPerSqm - before.costPerSqm;
    delta.itemCount = after.itemCount - before.itemCount;
    return delta;
}

std::string CostCalculator::toJson(const CostSummary& s) {
    nlohmann::json j;
    j["structural"] = s.structuralCost;
    j["mep"] = s.mepCost;
    j["finish"] = s.finishCost;
    j["other"] = s.otherCost;
    j["total"] = s.totalCost;
    j["costPerSqm"] = s.costPerSqm;
    j["itemCount"] = s.itemCount;
    j["currency"] = s.currency;
    return j.dump();
}

std::string CostCalculator::itemsToJson(const std::vector<CostItem>& items) {
    nlohmann::json arr = nlohmann::json::array();
    for (const auto& item : items) {
        arr.push_back({{"entityId", item.entityId}, {"category", item.category},
            {"description", item.description}, {"quantity", item.quantity},
            {"unit", item.unit}, {"unitPrice", item.unitPrice}, {"total", item.total}});
    }
    return arr.dump();
}

} // namespace bim
