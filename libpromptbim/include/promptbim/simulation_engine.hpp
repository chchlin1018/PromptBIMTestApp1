/**
 * simulation_engine.hpp — 4D Construction Simulation Engine (C++)
 *
 * Ports src/promptbim/bim/simulation/scheduler.py to C++17.
 * Component classification → phase sequencing → visibility states.
 */

#pragma once

#include <nlohmann/json.hpp>
#include <string>
#include <vector>
#include <map>
#include <optional>

namespace promptbim {

// -----------------------------------------------------------------------
// Data structures
// -----------------------------------------------------------------------

struct PhaseDefinition {
    std::string phase_id;
    std::string name;
    double duration_ratio;
    std::vector<std::string> keywords;
};

struct ScheduledPhase {
    std::string phase_id;
    std::string name;
    std::vector<std::string> components;
    int start_day = 0;
    int end_day   = 0;

    nlohmann::json to_json() const;
};

struct ConstructionSchedule {
    int total_days = 0;
    std::vector<ScheduledPhase> phases;

    nlohmann::json to_json() const;
};

// Component visibility state
enum class VisibilityState { HIDDEN, IN_PROGRESS, COMPLETED };

inline const char* visibility_to_string(VisibilityState s) {
    switch (s) {
        case VisibilityState::HIDDEN:      return "hidden";
        case VisibilityState::IN_PROGRESS: return "in_progress";
        case VisibilityState::COMPLETED:   return "completed";
    }
    return "hidden";
}

// -----------------------------------------------------------------------
// SimulationEngine
// -----------------------------------------------------------------------

class SimulationEngine {
public:
    SimulationEngine();

    // Generate schedule from component labels
    ConstructionSchedule generate_schedule(
        const std::vector<std::string>& component_labels,
        int total_days = 360,
        int num_stories = 1) const;

    // Classify a component label to a phase ID (e.g. "P06")
    std::optional<std::string> classify_component(const std::string& label) const;

    // Get visibility state for all components at a given day
    std::map<std::string, VisibilityState> get_visible_components(
        const ConstructionSchedule& schedule, int day) const;

    // Get active phase at a given day
    std::optional<ScheduledPhase> get_active_phase(
        const ConstructionSchedule& schedule, int day) const;

    // JSON interface (for C ABI)
    std::string generate_schedule_json(const std::string& plan_json,
                                        int total_days) const;

private:
    std::vector<PhaseDefinition> standard_phases_;
};

} // namespace promptbim
