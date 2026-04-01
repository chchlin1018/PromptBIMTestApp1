#pragma once
/// @file CostCalculator.h
/// @brief Cost calculation engine using Taiwan NT$ pricing for BIM entities.
///
/// Computes per-entity costs based on volume/area × unit price, categorizes by
/// structural/MEP/finish/other, and provides summary and delta analysis.

#include "BIMEntity.h"
#include "PropertyManager.h"
#include <vector>

namespace bim {

/// @brief Cost breakdown for a single entity.
struct CostItem {
    std::string entityId;       ///< Entity ID this cost belongs to
    std::string category;       ///< Cost category: "structural", "mep", "finish", "other"
    std::string description;    ///< Human-readable cost description
    double quantity = 0.0;      ///< Quantity (volume in m³ or area in m²)
    std::string unit;           ///< Unit of measurement (m³, m², ea)
    double unitPrice = 0.0;     ///< Price per unit in NT$
    double total = 0.0;         ///< Total cost = quantity × unitPrice (NT$)
};

/// @brief Aggregated cost summary across all entities.
struct CostSummary {
    double structuralCost = 0.0; ///< Total structural cost (NT$)
    double mepCost = 0.0;       ///< Total MEP cost (NT$)
    double finishCost = 0.0;    ///< Total finish cost (NT$)
    double otherCost = 0.0;     ///< Total other/generic cost (NT$)
    double totalCost = 0.0;     ///< Grand total (NT$)
    double costPerSqm = 0.0;    ///< Cost per square meter (NT$/m²)
    int itemCount = 0;          ///< Number of cost items
    std::string currency = "NT$"; ///< Currency denomination
};

/// @brief Cost calculation engine for BIM projects (Taiwan NT$ pricing).
///
/// Uses PropertyManager for unit price lookups. Supports per-entity cost,
/// batch calculation, summary, pipe routing cost, and before/after deltas.
class CostCalculator {
public:
    /// @brief Construct with a PropertyManager for unit price lookups.
    /// @param props Reference to PropertyManager containing material prices
    explicit CostCalculator(const PropertyManager& props);

    /// @brief Calculate cost for a single BIM entity based on volume × unit price.
    /// @param entity The entity to price
    /// @return CostItem with category, quantity, unit price, and total
    [[nodiscard]] CostItem calculateEntityCost(const BIMEntity& entity) const;

    /// @brief Calculate costs for a batch of entities. Skips null pointers.
    /// @param entities Vector of entity pointers (nulls are safely skipped)
    /// @return Vector of CostItem results
    [[nodiscard]] std::vector<CostItem> calculateAll(const std::vector<const BIMEntity*>& entities) const;

    /// @brief Aggregate cost items into a summary by category.
    /// @param items Vector of CostItem to summarize
    /// @param totalFloorArea Total floor area in m² (0 = skip per-sqm calculation)
    /// @return CostSummary with category breakdowns and totals
    [[nodiscard]] CostSummary summarize(const std::vector<CostItem>& items, double totalFloorArea = 0.0) const;

    /// @brief Calculate piping cost between two entities based on distance.
    /// @param from Source entity
    /// @param to Destination entity
    /// @param costPerMeter Cost per meter of pipe (default NT$3,500)
    /// @return Total pipe cost in NT$
    [[nodiscard]] double pipeCost(const BIMEntity& from, const BIMEntity& to, double costPerMeter = 3500.0) const;

    /// @brief Compute cost delta between two summaries (after - before).
    /// @param before Cost summary before changes
    /// @param after Cost summary after changes
    /// @return CostSummary representing the difference
    [[nodiscard]] CostSummary costDelta(const CostSummary& before, const CostSummary& after) const;

    /// @brief Serialize a CostSummary to JSON string.
    [[nodiscard]] static std::string toJson(const CostSummary& summary);
    /// @brief Serialize a vector of CostItems to JSON string.
    [[nodiscard]] static std::string itemsToJson(const std::vector<CostItem>& items);

private:
    const PropertyManager& m_props;
    /// @brief Look up unit price for an entity based on its type and properties.
    [[nodiscard]] double lookupUnitPrice(const BIMEntity& entity) const;
    /// @brief Categorize an entity type into "structural", "mep", "finish", or "other".
    [[nodiscard]] std::string categorize(EntityType type) const noexcept;
};

} // namespace bim
