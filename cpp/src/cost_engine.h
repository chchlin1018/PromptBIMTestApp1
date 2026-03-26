#pragma once
// PromptBIM C++ Core — Cost Engine (成本估算)
// Estimates construction cost based on building parameters

#include <string>
#include <vector>

namespace promptbim {

struct CostBreakdown {
    double structure_cost = 0.0;     // 結構成本 (NTD)
    double exterior_cost = 0.0;      // 外裝成本
    double interior_cost = 0.0;      // 內裝成本
    double mep_cost = 0.0;           // 機電成本
    double total_cost = 0.0;         // 總成本
    double cost_per_sqm = 0.0;       // 每坪造價
    std::string currency = "NTD";
};

struct BuildingParams {
    double total_floor_area_sqm = 0.0;
    int num_stories = 1;
    std::string building_type = "residential";  // residential/commercial/industrial
    std::string structure_type = "rc";           // rc/steel/wood
    int quality_level = 3;                       // 1-5 (1=basic, 5=premium)
};

class CostEngine {
public:
    CostEngine() = default;
    ~CostEngine() = default;

    /// Estimate construction cost
    CostBreakdown estimate(const BuildingParams& params) const;

    /// Get engine version
    static std::string version();
};

} // namespace promptbim
