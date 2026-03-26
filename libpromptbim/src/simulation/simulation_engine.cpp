/**
 * simulation_engine.cpp — 4D Construction Simulation Engine (C++)
 *
 * Ports src/promptbim/bim/simulation/scheduler.py to C++17.
 * Features:
 *   - 16 standard construction phases with duration ratios
 *   - Component label classification (pattern matching)
 *   - Phase sequencing with story-count scaling
 *   - Day-based visibility state queries
 */

#include "promptbim/simulation_engine.hpp"
#include "promptbim/promptbim.h"

#include <algorithm>
#include <cmath>
#include <cstring>

namespace promptbim {

// -----------------------------------------------------------------------
// ScheduledPhase / ConstructionSchedule serialization
// -----------------------------------------------------------------------

nlohmann::json ScheduledPhase::to_json() const {
    return {
        {"phase_id",   phase_id},
        {"name",       name},
        {"components", components},
        {"start_day",  start_day},
        {"end_day",    end_day},
    };
}

nlohmann::json ConstructionSchedule::to_json() const {
    nlohmann::json arr = nlohmann::json::array();
    for (const auto& p : phases) arr.push_back(p.to_json());
    return {
        {"total_days", total_days},
        {"phases",     arr},
    };
}

// -----------------------------------------------------------------------
// 16 Standard construction phases
// -----------------------------------------------------------------------

static std::vector<PhaseDefinition> make_standard_phases() {
    return {
        {"P01", "Site Preparation",    0.05, {"site"}},
        {"P02", "Foundation",          0.10, {"foundation", "footing", "pile", "ground_slab"}},
        {"P03", "Substructure",        0.08, {"basement"}},
        {"P04", "Columns",             0.10, {"column"}},
        {"P05", "Beams",               0.08, {"beam"}},
        {"P06", "Floor Slabs",         0.08, {"slab"}},
        {"P07", "Shear Walls/Core",    0.05, {"shear"}},
        {"P08", "Roof",                0.04, {"roof"}},
        {"P09", "Exterior Walls",      0.08, {"wall"}},
        {"P10", "Doors & Windows",     0.05, {"door", "window"}},
        {"P11", "MEP Rough-in",        0.08, {"duct", "pipe", "cable"}},
        {"P12", "Partition Walls",     0.05, {"partition", "interior"}},
        {"P13", "Elevators",           0.04, {"elevator", "escalator"}},
        {"P14", "Ceiling & Flooring",  0.05, {"ceiling", "floor", "covering"}},
        {"P15", "Fixtures & Equipment",0.04, {"sanitary", "furniture"}},
        {"P16", "MEP Finish",          0.03, {"light", "fire", "sprinkler"}},
    };
}

// -----------------------------------------------------------------------
// Construction
// -----------------------------------------------------------------------

SimulationEngine::SimulationEngine()
    : standard_phases_(make_standard_phases())
{}

// -----------------------------------------------------------------------
// Component classification
// -----------------------------------------------------------------------

std::optional<std::string> SimulationEngine::classify_component(
    const std::string& label) const
{
    // Convert to lowercase
    std::string lower = label;
    std::transform(lower.begin(), lower.end(), lower.begin(),
                   [](unsigned char c){ return std::tolower(c); });

    // Special cases first (more specific matches before general ones)
    if (lower.find("roof") != std::string::npos) return "P08";
    if (lower.find("ground_slab") != std::string::npos) return "P02";

    if (lower.find("slab") != std::string::npos) return "P06";

    if (lower.find("wall") != std::string::npos) {
        if (lower.find("partition") != std::string::npos ||
            lower.find("interior") != std::string::npos)
            return "P12";
        return "P09"; // default: exterior wall
    }

    if (lower.find("column") != std::string::npos) return "P04";
    if (lower.find("beam") != std::string::npos) return "P05";

    if (lower.find("door") != std::string::npos ||
        lower.find("window") != std::string::npos)
        return "P10";

    if (lower.find("duct") != std::string::npos ||
        lower.find("pipe") != std::string::npos ||
        lower.find("cable") != std::string::npos)
        return "P11";

    if (lower.find("elevator") != std::string::npos ||
        lower.find("escalator") != std::string::npos)
        return "P13";

    if (lower.find("ceiling") != std::string::npos ||
        lower.find("covering") != std::string::npos)
        return "P14";
    // Note: "floor" alone not matched here to avoid slab/floor confusion
    // (floor_tile, flooring → P14)
    if (lower.find("flooring") != std::string::npos ||
        lower.find("floor_tile") != std::string::npos)
        return "P14";

    if (lower.find("sanitary") != std::string::npos ||
        lower.find("furniture") != std::string::npos)
        return "P15";

    if (lower.find("light") != std::string::npos ||
        lower.find("fire") != std::string::npos ||
        lower.find("sprinkler") != std::string::npos)
        return "P16";

    return std::nullopt;
}

// -----------------------------------------------------------------------
// Schedule generation
// -----------------------------------------------------------------------

ConstructionSchedule SimulationEngine::generate_schedule(
    const std::vector<std::string>& component_labels,
    int total_days,
    int num_stories) const
{
    // Classify components by phase
    std::map<std::string, std::vector<std::string>> phase_components;
    for (const auto& label : component_labels) {
        auto pid = classify_component(label);
        if (pid) {
            phase_components[*pid].push_back(label);
        }
    }

    // Scale duration by building size
    double scale = std::max(1.0, static_cast<double>(num_stories) / 3.0);
    double adjusted_days = total_days * scale;

    // Build schedule: iterate phases in order
    ConstructionSchedule schedule;
    schedule.total_days = static_cast<int>(adjusted_days);
    int current_day = 0;

    // Always include P01 (site preparation)
    bool has_p01 = phase_components.count("P01") > 0;

    for (const auto& pdef : standard_phases_) {
        auto it = phase_components.find(pdef.phase_id);
        bool has_components = (it != phase_components.end());

        // Include P01 even without explicit components
        if (!has_components && pdef.phase_id != "P01") continue;
        if (!has_components && pdef.phase_id == "P01" && has_p01) continue;

        int duration = std::max(1,
            static_cast<int>(std::round(adjusted_days * pdef.duration_ratio)));

        ScheduledPhase sp;
        sp.phase_id  = pdef.phase_id;
        sp.name      = pdef.name;
        sp.start_day = current_day;
        sp.end_day   = current_day + duration;

        if (has_components) {
            sp.components = it->second;
        }

        schedule.phases.push_back(sp);
        current_day += duration;
    }

    // Update total_days to actual scheduled end
    if (!schedule.phases.empty()) {
        schedule.total_days = schedule.phases.back().end_day;
    }

    return schedule;
}

// -----------------------------------------------------------------------
// Visibility queries
// -----------------------------------------------------------------------

std::map<std::string, VisibilityState> SimulationEngine::get_visible_components(
    const ConstructionSchedule& schedule, int day) const
{
    std::map<std::string, VisibilityState> result;
    for (const auto& sp : schedule.phases) {
        for (const auto& comp : sp.components) {
            if (day < sp.start_day) {
                result[comp] = VisibilityState::HIDDEN;
            } else if (day < sp.end_day) {
                result[comp] = VisibilityState::IN_PROGRESS;
            } else {
                result[comp] = VisibilityState::COMPLETED;
            }
        }
    }
    return result;
}

std::optional<ScheduledPhase> SimulationEngine::get_active_phase(
    const ConstructionSchedule& schedule, int day) const
{
    for (const auto& sp : schedule.phases) {
        if (day >= sp.start_day && day < sp.end_day) {
            return sp;
        }
    }
    return std::nullopt;
}

// -----------------------------------------------------------------------
// JSON interface
// -----------------------------------------------------------------------

std::string SimulationEngine::generate_schedule_json(
    const std::string& plan_json, int total_days) const
{
    nlohmann::json plan;
    try {
        plan = nlohmann::json::parse(plan_json);
    } catch (const nlohmann::json::exception& e) {
        return nlohmann::json{{"error", std::string("JSON parse error: ") + e.what()}}.dump();
    }

    // Extract component labels from plan
    std::vector<std::string> labels;
    int num_stories = 0;

    if (plan.contains("components") && plan["components"].is_array()) {
        for (const auto& comp : plan["components"]) {
            if (comp.is_string()) {
                labels.push_back(comp.get<std::string>());
            } else if (comp.contains("label")) {
                labels.push_back(comp["label"].get<std::string>());
            }
        }
    }

    // Also extract from stories structure
    if (plan.contains("stories") && plan["stories"].is_array()) {
        num_stories = static_cast<int>(plan["stories"].size());
        for (const auto& story : plan["stories"]) {
            std::string sn = story.value("name", "");
            // Add implicit components: slab, walls
            if (story.contains("slab_boundary"))
                labels.push_back("Slab-" + sn);
            if (story.contains("walls")) {
                for (size_t i = 0; i < story["walls"].size(); ++i) {
                    std::string wt = story["walls"][i].value("wall_type", "exterior");
                    labels.push_back("Wall-" + wt + "-" + sn + "-" + std::to_string(i));
                }
            }
            if (story.contains("openings")) {
                for (size_t i = 0; i < story["openings"].size(); ++i) {
                    std::string ot = story["openings"][i].value("opening_type", "door");
                    labels.push_back(ot + "-" + sn + "-" + std::to_string(i));
                }
            }
        }
    }

    if (plan.contains("building_footprint"))
        labels.push_back("Roof");

    auto schedule = generate_schedule(labels, total_days, std::max(1, num_stories));
    return schedule.to_json().dump();
}

} // namespace promptbim

// -----------------------------------------------------------------------
// C ABI
// -----------------------------------------------------------------------

char* pb_generate_schedule(const char* plan_json, int total_days) {
    if (!plan_json) return nullptr;
    try {
        promptbim::SimulationEngine engine;
        std::string result = engine.generate_schedule_json(plan_json, total_days);
        char* out = static_cast<char*>(std::malloc(result.size() + 1));
        if (!out) return nullptr;
        std::memcpy(out, result.data(), result.size() + 1);
        return out;
    } catch (...) {
        return nullptr;
    }
}
