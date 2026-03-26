#include "cost_engine.h"

namespace promptbim {

CostBreakdown CostEngine::estimate(const BuildingParams& params) const {
    CostBreakdown result;
    result.currency = "NTD";

    // Base cost per sqm (NTD) by structure type
    double base_cost_per_sqm = 0.0;
    if (params.structure_type == "rc") {
        base_cost_per_sqm = 85000.0;  // RC 造
    } else if (params.structure_type == "steel") {
        base_cost_per_sqm = 95000.0;  // 鋼構
    } else if (params.structure_type == "wood") {
        base_cost_per_sqm = 75000.0;  // 木造
    } else {
        base_cost_per_sqm = 85000.0;  // default RC
    }

    // Quality multiplier
    double quality_mult = 0.7 + (params.quality_level - 1) * 0.15;

    // Building type multiplier
    double type_mult = 1.0;
    if (params.building_type == "commercial") {
        type_mult = 1.15;
    } else if (params.building_type == "industrial") {
        type_mult = 0.85;
    }

    // Height premium (>5 stories)
    double height_mult = 1.0;
    if (params.num_stories > 5) {
        height_mult = 1.0 + (params.num_stories - 5) * 0.02;
    }

    double adjusted_cost = base_cost_per_sqm * quality_mult * type_mult * height_mult;

    // Cost breakdown ratios
    result.structure_cost = params.total_floor_area_sqm * adjusted_cost * 0.40;
    result.exterior_cost  = params.total_floor_area_sqm * adjusted_cost * 0.15;
    result.interior_cost  = params.total_floor_area_sqm * adjusted_cost * 0.25;
    result.mep_cost       = params.total_floor_area_sqm * adjusted_cost * 0.20;
    result.total_cost     = result.structure_cost + result.exterior_cost
                          + result.interior_cost + result.mep_cost;
    result.cost_per_sqm   = (params.total_floor_area_sqm > 0)
                          ? result.total_cost / params.total_floor_area_sqm
                          : 0.0;

    return result;
}

std::string CostEngine::version() {
    return "3.0.0";
}

} // namespace promptbim
