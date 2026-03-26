/**
 * cost_engine.cpp — Construction Cost Estimation Engine (C++)
 *
 * Ports src/promptbim/bim/cost/ (QTO + estimator + unit_prices_tw) to C++17.
 * Input/output via nlohmann/json strings. No external dependencies.
 */

#include "promptbim/cost_engine.hpp"
#include "promptbim/geometry.hpp"
#include "promptbim/promptbim.h"

#include <cmath>
#include <cstring>
#include <map>
#include <algorithm>

namespace promptbim {

// ---------------------------------------------------------------------------
// Unit prices (TWD, 2025-2026 POC-grade)
// ---------------------------------------------------------------------------

struct UnitPriceEntry {
    double      price;
    std::string unit;
    std::string category;
    std::string desc;
};

static const std::map<std::string, UnitPriceEntry> UNIT_PRICES = {
    {"brick_wall_sqm",       {1800,  "m2",   "envelope",   "1B brick wall"}},
    {"partition_sqm",        {1200,  "m2",   "interior",   "Light partition wall"}},
    {"slab_sqm",             {2800,  "m2",   "structure",  "RC slab"}},
    {"door_single",          {8000,  "unit", "door_window","Aluminium door"}},
    {"window_sliding_sqm",   {6500,  "m2",   "door_window","Aluminium sliding window"}},
    {"roof_flat_sqm",        {2200,  "m2",   "roof",       "Flat roof waterproofing"}},
    {"hvac_sqm",             {3500,  "m2",   "mep",        "HVAC system"}},
    {"plumbing_sqm",         {1200,  "m2",   "mep",        "Plumbing"}},
    {"electrical_sqm",       {2000,  "m2",   "mep",        "Electrical system"}},
    {"fire_protection_sqm",  {800,   "m2",   "mep",        "Fire protection"}},
    {"site_work_sqm",        {1500,  "m2",   "site",       "Site work"}},
    {"ceiling_sqm",          {800,   "m2",   "interior",   "Light-gauge steel ceiling"}},
    {"floor_tile_sqm",       {1500,  "m2",   "interior",   "Floor tile"}},
};

// QTO category → price key
static const std::map<std::string, std::string> QTO_PRICE_MAP = {
    {"wall_exterior", "brick_wall_sqm"},
    {"wall_interior", "partition_sqm"},
    {"slab",          "slab_sqm"},
    {"door",          "door_single"},
    {"window",        "window_sliding_sqm"},
    {"roof",          "roof_flat_sqm"},
    {"mep_hvac",      "hvac_sqm"},
    {"mep_plumbing",  "plumbing_sqm"},
    {"mep_electrical","electrical_sqm"},
    {"mep_fire",      "fire_protection_sqm"},
    {"site_work",     "site_work_sqm"},
};

// Category display labels
static const std::map<std::string, std::string> CATEGORY_LABELS = {
    {"structure",   "Structure"},
    {"envelope",    "Envelope"},
    {"interior",    "Interior Finishes"},
    {"door_window", "Doors & Windows"},
    {"mep",         "MEP Systems"},
    {"equipment",   "Equipment"},
    {"roof",        "Roof"},
    {"site",        "Site Work"},
    {"monitoring",  "Smart Monitoring"},
};

// ---------------------------------------------------------------------------
// Geometry helpers — now using shared geometry module
// ---------------------------------------------------------------------------

static double poly_area(const nlohmann::json& coords) {
    return promptbim::geometry::poly_area(coords);
}

static double wall_length(const nlohmann::json& wall) {
    return promptbim::geometry::wall_length(wall);
}

// ---------------------------------------------------------------------------
// QTO extraction
// ---------------------------------------------------------------------------

std::vector<CostEngine::QTOItem>
CostEngine::extract_qto(const nlohmann::json& plan) const
{
    std::vector<QTOItem> items;
    double total_floor_area = 0.0;

    if (!plan.contains("stories")) return items;

    for (const auto& story : plan["stories"]) {
        std::string sn = story.value("name", "");
        double h_m     = story.value("height_m", 3.0);

        // Walls
        if (story.contains("walls")) {
            int wi = 0;
            for (const auto& w : story["walls"]) {
                double length = wall_length(w);
                double area   = length * h_m;
                std::string wall_type = w.value("wall_type", "exterior");
                std::string cat = (wall_type == "exterior") ? "wall_exterior" : "wall_interior";
                items.push_back({cat, "Wall-" + sn + "-" + std::to_string(wi),
                                 area, "m2", sn});
                ++wi;
            }
        }

        // Slab
        nlohmann::json slab_bnd = nlohmann::json::array();
        if (story.contains("slab_boundary") && story["slab_boundary"].is_array())
            slab_bnd = story["slab_boundary"];
        else if (plan.contains("building_footprint"))
            slab_bnd = plan["building_footprint"];

        double slab_area = poly_area(slab_bnd);
        if (slab_area > 0.0) {
            items.push_back({"slab", "Slab-" + sn, slab_area, "m2", sn});
            total_floor_area += slab_area;
        }

        // Doors & Windows
        if (story.contains("openings")) {
            int oi = 0;
            for (const auto& o : story["openings"]) {
                std::string ot = o.value("opening_type", "window");
                if (ot == "door") {
                    items.push_back({"door", "Door-" + sn + "-" + std::to_string(oi),
                                     1.0, "unit", sn});
                } else {
                    double w = o.value("width_m", 1.5);
                    double hh = o.value("height_m", 1.2);
                    items.push_back({"window", "Window-" + sn + "-" + std::to_string(oi),
                                     w * hh, "m2", sn});
                }
                ++oi;
            }
        }
    }

    // Roof
    if (plan.contains("building_footprint")) {
        double roof_area = poly_area(plan["building_footprint"]);
        if (roof_area > 0.0)
            items.push_back({"roof", "Roof", roof_area, "m2", "Roof"});
    }

    // MEP (allowance based on total floor area)
    if (total_floor_area > 0.0) {
        items.push_back({"mep_hvac",       "HVAC System",       total_floor_area, "m2", ""});
        items.push_back({"mep_plumbing",   "Plumbing System",   total_floor_area, "m2", ""});
        items.push_back({"mep_electrical", "Electrical System", total_floor_area, "m2", ""});
        items.push_back({"mep_fire",       "Fire Protection",   total_floor_area, "m2", ""});
    }

    // Site work
    if (plan.contains("land_boundary") && plan.contains("building_footprint")) {
        double land_area = poly_area(plan["land_boundary"]);
        double fp_area   = poly_area(plan["building_footprint"]);
        double site_area = (land_area > fp_area) ? land_area - fp_area : 0.0;
        if (site_area > 0.0)
            items.push_back({"site_work", "Site Work", site_area, "m2", ""});
    }

    return items;
}

// ---------------------------------------------------------------------------
// Price items
// ---------------------------------------------------------------------------

std::vector<CostEngine::CostLineItem>
CostEngine::price_items(const std::vector<QTOItem>& qto) const
{
    std::vector<CostLineItem> result;
    for (const auto& qi : qto) {
        auto pit = QTO_PRICE_MAP.find(qi.category);
        if (pit == QTO_PRICE_MAP.end()) continue;
        const std::string& price_key = pit->second;

        auto eit = UNIT_PRICES.find(price_key);
        if (eit == UNIT_PRICES.end()) continue;

        const auto& entry = eit->second;
        double total = qi.quantity * entry.price;
        result.push_back({entry.category, qi.name, qi.quantity,
                          qi.unit, entry.price, total, qi.category});
    }
    return result;
}

// ---------------------------------------------------------------------------
// Interior finish allowance (ceiling + floor tile per slab)
// ---------------------------------------------------------------------------

std::vector<CostEngine::CostLineItem>
CostEngine::interior_finish_allowance(const std::vector<QTOItem>& qto) const
{
    std::vector<CostLineItem> result;
    double ceiling_price = UNIT_PRICES.at("ceiling_sqm").price;
    double tile_price    = UNIT_PRICES.at("floor_tile_sqm").price;

    for (const auto& qi : qto) {
        if (qi.category != "slab") continue;
        double area = qi.quantity;

        result.push_back({"interior", "Ceiling-" + qi.story, area,
                          "m2", ceiling_price, area * ceiling_price, "ceiling"});
        result.push_back({"interior", "FloorTile-" + qi.story, area,
                          "m2", tile_price, area * tile_price, "floor_tile"});
    }
    return result;
}

// ---------------------------------------------------------------------------
// Main: estimate()
// ---------------------------------------------------------------------------

std::string CostEngine::estimate(const std::string& plan_json) const
{
    nlohmann::json plan;
    try {
        plan = nlohmann::json::parse(plan_json);
    } catch (const nlohmann::json::exception& e) {
        return nlohmann::json{{"error", std::string("JSON parse error: ") + e.what()}}.dump();
    }

    std::string project_name = plan.value("name", "Unnamed Project");

    auto qto          = extract_qto(plan);
    auto line_items   = price_items(qto);
    auto int_items    = interior_finish_allowance(qto);
    line_items.insert(line_items.end(), int_items.begin(), int_items.end());

    double total = 0.0;
    for (const auto& li : line_items) total += li.total;

    // Total floor area
    double total_floor_area = 0.0;
    for (const auto& qi : qto) {
        if (qi.category == "slab") total_floor_area += qi.quantity;
    }

    // Breakdown by category
    std::map<std::string, double> cat_totals;
    for (const auto& li : line_items) {
        std::string cat = li.category;
        // Use price_key to get category if needed
        auto eit = UNIT_PRICES.find(li.price_key);
        if (eit != UNIT_PRICES.end()) cat = eit->second.category;
        cat_totals[cat] += li.total;
    }

    nlohmann::json breakdown_arr = nlohmann::json::array();
    // Sort by cost descending
    std::vector<std::pair<std::string,double>> sorted_cats(cat_totals.begin(), cat_totals.end());
    std::sort(sorted_cats.begin(), sorted_cats.end(),
              [](const auto& a, const auto& b){ return a.second > b.second; });

    for (const auto& [cat, cost] : sorted_cats) {
        auto lit = CATEGORY_LABELS.find(cat);
        std::string label = (lit != CATEGORY_LABELS.end()) ? lit->second : cat;
        breakdown_arr.push_back({
            {"category", label},
            {"cost",     static_cast<long long>(std::round(cost))},
            {"ratio",    total > 0 ? std::round(cost / total * 1000.0) / 1000.0 : 0.0},
        });
    }

    double cost_per_sqm = (total_floor_area > 0) ? total / total_floor_area : 0.0;

    nlohmann::json out = {
        {"project",             project_name},
        {"total_cost_twd",      static_cast<long long>(std::round(total))},
        {"total_floor_area_sqm",std::round(total_floor_area * 10.0) / 10.0},
        {"cost_per_sqm_twd",    static_cast<long long>(std::round(cost_per_sqm))},
        {"breakdown",           breakdown_arr},
        {"notes",               "POC-grade estimate (+-30%), for early planning only"},
    };
    return out.dump();
}

} // namespace promptbim

// ---------------------------------------------------------------------------
// C ABI
// ---------------------------------------------------------------------------

char* pb_estimate_cost(const char* plan_json) {
    if (!plan_json) return nullptr;
    try {
        promptbim::CostEngine engine;
        std::string result = engine.estimate(plan_json);
        char* out = static_cast<char*>(std::malloc(result.size() + 1));
        if (!out) return nullptr;
        std::memcpy(out, result.data(), result.size() + 1);
        return out;
    } catch (...) {
        return nullptr;
    }
}
