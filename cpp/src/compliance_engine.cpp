#include "compliance_engine.h"
#include <sstream>

namespace promptbim {

ComplianceResult ComplianceEngine::check(
    double land_area_sqm,
    double building_footprint_sqm,
    double total_floor_area_sqm,
    double building_height_m,
    const ZoningParams& zoning
) const {
    ComplianceResult result;

    // Calculate ratios
    result.bcr = (land_area_sqm > 0) ? building_footprint_sqm / land_area_sqm : 0.0;
    result.far_ratio = (land_area_sqm > 0) ? total_floor_area_sqm / land_area_sqm : 0.0;
    result.height_m = building_height_m;
    result.passed = true;

    // BCR check
    if (result.bcr > zoning.bcr_limit) {
        std::ostringstream oss;
        oss << "BCR " << result.bcr << " exceeds limit " << zoning.bcr_limit;
        result.violations.push_back(oss.str());
        result.passed = false;
    }

    // FAR check
    if (result.far_ratio > zoning.far_limit) {
        std::ostringstream oss;
        oss << "FAR " << result.far_ratio << " exceeds limit " << zoning.far_limit;
        result.violations.push_back(oss.str());
        result.passed = false;
    }

    // Height check
    if (building_height_m > zoning.height_limit_m) {
        std::ostringstream oss;
        oss << "Height " << building_height_m << "m exceeds limit " << zoning.height_limit_m << "m";
        result.violations.push_back(oss.str());
        result.passed = false;
    }

    // Warnings
    if (result.bcr > zoning.bcr_limit * 0.9 && result.bcr <= zoning.bcr_limit) {
        result.warnings.push_back("BCR near limit (>90%)");
    }
    if (result.far_ratio > zoning.far_limit * 0.9 && result.far_ratio <= zoning.far_limit) {
        result.warnings.push_back("FAR near limit (>90%)");
    }

    return result;
}

std::string ComplianceEngine::version() {
    return "3.0.0";
}

} // namespace promptbim
