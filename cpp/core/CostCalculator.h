#pragma once
// CostCalculator.h — Cost calculation engine (NT$ Taiwan pricing)

#include "BIMEntity.h"
#include "PropertyManager.h"
#include <vector>

namespace bim {

struct CostItem {
    std::string entityId;
    std::string category;  // structural, mep, finish, etc.
    std::string description;
    double quantity = 0.0;
    std::string unit;
    double unitPrice = 0.0;
    double total = 0.0;
};

struct CostSummary {
    double structuralCost = 0.0;
    double mepCost = 0.0;
    double finishCost = 0.0;
    double otherCost = 0.0;
    double totalCost = 0.0;
    double costPerSqm = 0.0;
    int itemCount = 0;
    std::string currency = "NT$";
};

class CostCalculator {
public:
    explicit CostCalculator(const PropertyManager& props);

    // Calculate cost for a single entity
    [[nodiscard]] CostItem calculateEntityCost(const BIMEntity& entity) const;

    // Calculate cost for all entities
    [[nodiscard]] std::vector<CostItem> calculateAll(const std::vector<const BIMEntity*>& entities) const;

    // Summary
    [[nodiscard]] CostSummary summarize(const std::vector<CostItem>& items, double totalFloorArea = 0.0) const;

    // Pipe cost between two entities
    [[nodiscard]] double pipeCost(const BIMEntity& from, const BIMEntity& to, double costPerMeter = 3500.0) const;

    // Cost delta
    [[nodiscard]] CostSummary costDelta(const CostSummary& before, const CostSummary& after) const;

    // Serialization
    [[nodiscard]] static std::string toJson(const CostSummary& summary);
    [[nodiscard]] static std::string itemsToJson(const std::vector<CostItem>& items);

private:
    const PropertyManager& m_props;
    [[nodiscard]] double lookupUnitPrice(const BIMEntity& entity) const;
    [[nodiscard]] std::string categorize(EntityType type) const noexcept;
};

} // namespace bim
