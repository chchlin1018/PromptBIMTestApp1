#pragma once
// PromptBIM C++ Core — Compliance Engine (法規引擎)
// Checks building plans against Taiwan building codes

#include <string>
#include <vector>

namespace promptbim {

struct ComplianceResult {
    bool passed = false;
    double bcr = 0.0;          // Building Coverage Ratio (建蔽率)
    double far_ratio = 0.0;    // Floor Area Ratio (容積率)
    double height_m = 0.0;     // Building height (公尺)
    std::vector<std::string> violations;
    std::vector<std::string> warnings;
};

struct ZoningParams {
    std::string zone_type = "residential";
    double bcr_limit = 0.6;
    double far_limit = 2.0;
    double height_limit_m = 15.0;
    double setback_front_m = 5.0;
    double setback_back_m = 3.0;
    double setback_left_m = 2.0;
    double setback_right_m = 2.0;
};

class ComplianceEngine {
public:
    ComplianceEngine() = default;
    ~ComplianceEngine() = default;

    /// Check a building plan against zoning rules
    ComplianceResult check(
        double land_area_sqm,
        double building_footprint_sqm,
        double total_floor_area_sqm,
        double building_height_m,
        const ZoningParams& zoning
    ) const;

    /// Get engine version
    static std::string version();
};

} // namespace promptbim
