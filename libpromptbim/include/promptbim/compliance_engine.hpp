/**
 * compliance_engine.hpp — Taiwan Building Code Compliance Engine (C++)
 *
 * Ports the 15+ rule checks from src/promptbim/codes/ to native C++.
 * Input/output via nlohmann/json — fully self-contained, no Python dep.
 */

#pragma once

#include <string>
#include <vector>
#include <nlohmann/json.hpp>

namespace promptbim {

// ---------------------------------------------------------------------------
// Severity
// ---------------------------------------------------------------------------

enum class Severity { PASS, WARNING, FAIL, INFO };

inline std::string severity_str(Severity s) {
    switch (s) {
        case Severity::PASS:    return "pass";
        case Severity::WARNING: return "warning";
        case Severity::FAIL:    return "fail";
        case Severity::INFO:    return "info";
    }
    return "info";
}

// ---------------------------------------------------------------------------
// CheckResult
// ---------------------------------------------------------------------------

struct CheckResult {
    std::string rule_id;
    std::string rule_name;
    std::string law_reference;
    Severity    severity = Severity::PASS;
    std::string message;
    double      actual_value = 0.0;
    double      limit_value  = 0.0;
    std::string suggestion;

    nlohmann::json to_json() const {
        return {
            {"rule_id",      rule_id},
            {"rule_name",    rule_name},
            {"law_reference",law_reference},
            {"severity",     severity_str(severity)},
            {"message",      message},
            {"actual_value", actual_value},
            {"limit_value",  limit_value},
            {"suggestion",   suggestion},
        };
    }
};

// ---------------------------------------------------------------------------
// ComplianceEngine
// ---------------------------------------------------------------------------

class ComplianceEngine {
public:
    /**
     * Run all 15+ Taiwan building code rules.
     *
     * @param plan_json   BuildingPlan as JSON string
     * @param land_json   LandParcel  as JSON string
     * @param zoning_json ZoningInfo  as JSON string
     * @return            Compliance summary as JSON string
     */
    std::string check(
        const std::string& plan_json,
        const std::string& land_json,
        const std::string& zoning_json
    ) const;

private:
    // --- rule helpers ---
    static CheckResult check_bcr(
        const nlohmann::json& plan,
        const nlohmann::json& land,
        const nlohmann::json& zoning);

    static CheckResult check_far(
        const nlohmann::json& plan,
        const nlohmann::json& land,
        const nlohmann::json& zoning);

    static CheckResult check_height(
        const nlohmann::json& plan,
        const nlohmann::json& zoning);

    static CheckResult check_stairs(
        const nlohmann::json& plan);

    static CheckResult check_corridor(
        const nlohmann::json& plan);

    static CheckResult check_ceiling_height(
        const nlohmann::json& plan);

    static CheckResult check_elevator(
        const nlohmann::json& plan);

    static CheckResult check_parking(
        const nlohmann::json& plan,
        const nlohmann::json& land);

    static CheckResult check_fire_construction(
        const nlohmann::json& plan);

    static CheckResult check_fire_compartment(
        const nlohmann::json& plan);

    static CheckResult check_fire_escape(
        const nlohmann::json& plan);

    static CheckResult check_two_stairs(
        const nlohmann::json& plan);

    static CheckResult check_safety_stair(
        const nlohmann::json& plan);

    static CheckResult check_seismic(
        const nlohmann::json& plan);

    static CheckResult check_accessibility(
        const nlohmann::json& plan);

    // --- geometry helpers ---
    static double poly_area(const nlohmann::json& coords);
    static double total_floor_area(const nlohmann::json& plan);
    static double footprint_area(const nlohmann::json& plan);
    static double building_height(const nlohmann::json& plan);
    static int    num_stories(const nlohmann::json& plan);
};

} // namespace promptbim
