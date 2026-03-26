/**
 * compliance_engine.cpp — Taiwan Building Code Compliance Engine (C++)
 *
 * Ports 15 rules from src/promptbim/codes/:
 *   tw_building_code.py  : BCR, FAR, Height, Stairs, Corridor, CeilingHeight,
 *                          Elevator, Parking
 *   tw_fire_code.py      : FireConstruction, FireCompartment, FireEscape,
 *                          TwoStairs, SafetyStair
 *   tw_seismic_code.py   : Seismic
 *   tw_accessibility_code.py : Accessibility
 *
 * Input / output: nlohmann/json strings.
 * No external dependencies beyond nlohmann/json and std C++17.
 */

#include "promptbim/compliance_engine.hpp"
#include "promptbim/promptbim.h"

#include <cmath>
#include <cstring>
#include <sstream>
#include <stdexcept>
#include <algorithm>

namespace promptbim {

// ---------------------------------------------------------------------------
// Geometry helpers
// ---------------------------------------------------------------------------

double ComplianceEngine::poly_area(const nlohmann::json& coords) {
    // Shoelace formula — coords is [[x,y], ...]
    if (!coords.is_array() || coords.size() < 3) return 0.0;
    double area = 0.0;
    const size_t n = coords.size();
    for (size_t i = 0; i < n; ++i) {
        size_t j = (i + 1) % n;
        double xi = coords[i][0].get<double>();
        double yi = coords[i][1].get<double>();
        double xj = coords[j][0].get<double>();
        double yj = coords[j][1].get<double>();
        area += xi * yj - xj * yi;
    }
    return std::abs(area) / 2.0;
}

double ComplianceEngine::footprint_area(const nlohmann::json& plan) {
    if (plan.contains("building_footprint") && !plan["building_footprint"].is_null()) {
        return poly_area(plan["building_footprint"]);
    }
    return 0.0;
}

double ComplianceEngine::total_floor_area(const nlohmann::json& plan) {
    double total = 0.0;
    if (!plan.contains("stories")) return total;
    for (const auto& story : plan["stories"]) {
        if (story.contains("slab_boundary") && story["slab_boundary"].is_array()
                && story["slab_boundary"].size() >= 3) {
            total += poly_area(story["slab_boundary"]);
        } else if (story.contains("spaces")) {
            for (const auto& sp : story["spaces"]) {
                if (sp.contains("area_sqm"))
                    total += sp["area_sqm"].get<double>();
            }
        }
    }
    return total;
}

double ComplianceEngine::building_height(const nlohmann::json& plan) {
    if (!plan.contains("stories") || plan["stories"].empty()) return 0.0;
    const auto& top = plan["stories"].back();
    double elev = top.value("elevation_m", 0.0);
    double h    = top.value("height_m", 0.0);
    return elev + h;
}

int ComplianceEngine::num_stories(const nlohmann::json& plan) {
    if (!plan.contains("stories")) return 0;
    return static_cast<int>(plan["stories"].size());
}

// ---------------------------------------------------------------------------
// Rule helpers
// ---------------------------------------------------------------------------

static CheckResult make_pass(const std::string& rule_id,
                              const std::string& rule_name,
                              const std::string& law_ref,
                              const std::string& msg,
                              double actual = 0.0, double limit = 0.0)
{
    CheckResult r;
    r.rule_id       = rule_id;
    r.rule_name     = rule_name;
    r.law_reference = law_ref;
    r.severity      = Severity::PASS;
    r.message       = msg;
    r.actual_value  = actual;
    r.limit_value   = limit;
    return r;
}

static CheckResult make_fail(const std::string& rule_id,
                              const std::string& rule_name,
                              const std::string& law_ref,
                              const std::string& msg,
                              const std::string& suggestion = "",
                              double actual = 0.0, double limit = 0.0)
{
    CheckResult r;
    r.rule_id       = rule_id;
    r.rule_name     = rule_name;
    r.law_reference = law_ref;
    r.severity      = Severity::FAIL;
    r.message       = msg;
    r.suggestion    = suggestion;
    r.actual_value  = actual;
    r.limit_value   = limit;
    return r;
}

static CheckResult make_warning(const std::string& rule_id,
                                 const std::string& rule_name,
                                 const std::string& law_ref,
                                 const std::string& msg,
                                 double actual = 0.0, double limit = 0.0)
{
    CheckResult r;
    r.rule_id       = rule_id;
    r.rule_name     = rule_name;
    r.law_reference = law_ref;
    r.severity      = Severity::WARNING;
    r.message       = msg;
    r.actual_value  = actual;
    r.limit_value   = limit;
    return r;
}

static CheckResult make_info(const std::string& rule_id,
                              const std::string& rule_name,
                              const std::string& law_ref,
                              const std::string& msg,
                              double actual = 0.0, double limit = 0.0)
{
    CheckResult r;
    r.rule_id       = rule_id;
    r.rule_name     = rule_name;
    r.law_reference = law_ref;
    r.severity      = Severity::INFO;
    r.message       = msg;
    r.actual_value  = actual;
    r.limit_value   = limit;
    return r;
}

// Convenience round-to-4 decimals
static double r4(double v) { return std::round(v * 10000.0) / 10000.0; }

// ---------------------------------------------------------------------------
// Rule 1: BCR — Art. 25
// ---------------------------------------------------------------------------

CheckResult ComplianceEngine::check_bcr(const nlohmann::json& plan,
                                         const nlohmann::json& land,
                                         const nlohmann::json& zoning)
{
    static const char* ID   = "TW-BTC-BCR";
    static const char* NAME = "建蔽率檢查";
    static const char* LAW  = "建築技術規則建築設計施工編 第25條";

    double land_area = land.value("area_sqm", 0.0);
    double fp_area   = footprint_area(plan);

    if (land_area <= 0.0)
        return make_info(ID, NAME, LAW, "土地面積為零，無法計算建蔽率");

    double actual = fp_area / land_area;
    double limit  = zoning.value("bcr_limit", 0.6);

    if (actual > limit)
        return make_fail(ID, NAME, LAW,
            "建蔽率 " + std::to_string(std::round(actual * 1000.0)/10.0) + "% 超過上限",
            "縮小建築投影面積", r4(actual), r4(limit));

    if (actual > limit * 0.95)
        return make_warning(ID, NAME, LAW,
            "建蔽率接近上限", r4(actual), r4(limit));

    return make_pass(ID, NAME, LAW,
        "建蔽率符合規定", r4(actual), r4(limit));
}

// ---------------------------------------------------------------------------
// Rule 2: FAR — Art. 161
// ---------------------------------------------------------------------------

CheckResult ComplianceEngine::check_far(const nlohmann::json& plan,
                                         const nlohmann::json& land,
                                         const nlohmann::json& zoning)
{
    static const char* ID   = "TW-BTC-FAR";
    static const char* NAME = "容積率檢查";
    static const char* LAW  = "建築技術規則建築設計施工編 第161條";

    double land_area  = land.value("area_sqm", 0.0);
    double total_area = total_floor_area(plan);

    if (land_area <= 0.0)
        return make_info(ID, NAME, LAW, "土地面積為零，無法計算容積率");

    double actual = total_area / land_area;
    double limit  = zoning.value("far_limit", 2.0);

    if (actual > limit)
        return make_fail(ID, NAME, LAW,
            "容積率超過上限", "減少樓層數或縮小各層面積", r4(actual), r4(limit));

    if (actual > limit * 0.95)
        return make_warning(ID, NAME, LAW, "容積率接近上限", r4(actual), r4(limit));

    return make_pass(ID, NAME, LAW, "容積率符合規定", r4(actual), r4(limit));
}

// ---------------------------------------------------------------------------
// Rule 3: Height Limit — Art. 24-1
// ---------------------------------------------------------------------------

CheckResult ComplianceEngine::check_height(const nlohmann::json& plan,
                                            const nlohmann::json& zoning)
{
    static const char* ID   = "TW-BTC-24-1";
    static const char* NAME = "建築物高度限制";
    static const char* LAW  = "建築技術規則建築設計施工編 第24條之一";

    double height = building_height(plan);
    double limit  = zoning.value("height_limit_m", 50.0);

    if (height > limit)
        return make_fail(ID, NAME, LAW,
            "建築高度超過限制", "減少樓層數或降低層高",
            std::round(height * 100.0) / 100.0,
            std::round(limit  * 100.0) / 100.0);

    if (height > limit * 0.95)
        return make_warning(ID, NAME, LAW, "建築高度接近限制", height, limit);

    return make_pass(ID, NAME, LAW, "建築高度符合規定", height, limit);
}

// ---------------------------------------------------------------------------
// Rule 4: Stairs — Art. 33
// ---------------------------------------------------------------------------

CheckResult ComplianceEngine::check_stairs(const nlohmann::json& plan) {
    static const char* ID   = "TW-BTC-33";
    static const char* NAME = "樓梯設置規定";
    static const char* LAW  = "建築技術規則建築設計施工編 第33條";

    int n = num_stories(plan);
    if (n <= 1)
        return make_pass(ID, NAME, LAW, "單層建築無樓梯要求");

    double total_area     = total_floor_area(plan);
    double area_per_floor = (n > 0) ? total_area / n : 0.0;

    if (area_per_floor > 200.0)
        return make_info(ID, NAME, LAW,
            "每層面積 > 200㎡，樓梯淨寬需 >= 1.2m、級高 <= 20cm、級深 >= 24cm",
            area_per_floor, 200.0);

    return make_info(ID, NAME, LAW,
        "每層面積 <= 200㎡，樓梯淨寬需 >= 0.75m",
        area_per_floor, 200.0);
}

// ---------------------------------------------------------------------------
// Rule 5: Corridor — Art. 92
// ---------------------------------------------------------------------------

CheckResult ComplianceEngine::check_corridor(const nlohmann::json& plan) {
    static const char* ID   = "TW-BTC-92";
    static const char* NAME = "走廊寬度規定";
    static const char* LAW  = "建築技術規則建築設計施工編 第92條";

    if (!plan.contains("stories"))
        return make_pass(ID, NAME, LAW, "走廊寬度符合規定（或無走廊空間）");

    for (const auto& story : plan["stories"]) {
        if (!story.contains("spaces")) continue;
        std::string story_name = story.value("name", "");
        for (const auto& sp : story["spaces"]) {
            std::string type = sp.value("space_type", "");
            if (type != "corridor") continue;
            if (!sp.contains("boundary") || sp["boundary"].size() < 2) continue;

            const auto& bnd = sp["boundary"];
            double xmin = bnd[0][0].get<double>(), xmax = xmin;
            double ymin = bnd[0][1].get<double>(), ymax = ymin;
            for (const auto& pt : bnd) {
                double x = pt[0].get<double>(), y = pt[1].get<double>();
                xmin = std::min(xmin, x); xmax = std::max(xmax, x);
                ymin = std::min(ymin, y); ymax = std::max(ymax, y);
            }
            double w = std::min(xmax - xmin, ymax - ymin);
            if (w < 1.2) {
                return make_fail(ID, NAME, LAW,
                    story_name + " 走廊寬度不足 1.2m",
                    "加寬走廊至 1.2m 以上", std::round(w * 100.0) / 100.0, 1.2);
            }
        }
    }
    return make_pass(ID, NAME, LAW, "走廊寬度符合規定（或無走廊空間）");
}

// ---------------------------------------------------------------------------
// Rule 6: Ceiling Height — Art. 26
// ---------------------------------------------------------------------------

CheckResult ComplianceEngine::check_ceiling_height(const nlohmann::json& plan) {
    static const char* ID   = "TW-BTC-26";
    static const char* NAME = "天花板高度規定";
    static const char* LAW  = "建築技術規則建築設計施工編 第26條";

    if (!plan.contains("stories"))
        return make_pass(ID, NAME, LAW, "天花板高度符合規定");

    for (const auto& story : plan["stories"]) {
        double h_m     = story.value("height_m", 3.0);
        double slab_t  = story.value("slab_thickness_m", 0.2);
        double net_h   = h_m - slab_t;
        std::string sn = story.value("name", "");

        if (net_h < 2.1) {
            return make_fail(ID, NAME, LAW,
                sn + " 淨高不足 2.1m（居室最低）",
                "增加層高或減少樓板厚度",
                std::round(net_h * 100.0) / 100.0, 2.1);
        }
    }
    return make_pass(ID, NAME, LAW, "天花板高度符合規定");
}

// ---------------------------------------------------------------------------
// Rule 7: Elevator — Art. 55-1
// ---------------------------------------------------------------------------

CheckResult ComplianceEngine::check_elevator(const nlohmann::json& plan) {
    static const char* ID   = "TW-BTC-55-1";
    static const char* NAME = "昇降設備設置規定";
    static const char* LAW  = "建築技術規則建築設計施工編 第55條之一";

    int n = num_stories(plan);
    if (n >= 6)
        return make_info(ID, NAME, LAW,
            "6 層以上建築需設置電梯，請確認設計圖說", static_cast<double>(n), 6.0);

    return make_pass(ID, NAME, LAW,
        "樓層數 " + std::to_string(n) + " 層，無強制電梯要求",
        static_cast<double>(n), 5.0);
}

// ---------------------------------------------------------------------------
// Rule 8: Parking — 都市計畫停車場設置標準
// ---------------------------------------------------------------------------

CheckResult ComplianceEngine::check_parking(const nlohmann::json& plan,
                                             const nlohmann::json& land)
{
    static const char* ID   = "TW-PK-01";
    static const char* NAME = "停車位設置規定";
    static const char* LAW  = "都市計畫停車場設置標準";

    double total_area = total_floor_area(plan);
    int    required   = static_cast<int>(total_area / 100.0);  // 1 per 100 sqm

    int    provided   = 0;
    if (plan.contains("parking_spaces"))
        provided = plan["parking_spaces"].get<int>();

    if (required == 0)
        return make_pass(ID, NAME, LAW, "樓地板面積小，無停車要求",
            static_cast<double>(provided), 0.0);

    if (provided < required)
        return make_fail(ID, NAME, LAW,
            "停車位不足（需 " + std::to_string(required) +
            " 位，提供 " + std::to_string(provided) + " 位）",
            "增加地下停車場或機械停車設備",
            static_cast<double>(provided), static_cast<double>(required));

    return make_pass(ID, NAME, LAW,
        "停車位符合規定",
        static_cast<double>(provided), static_cast<double>(required));
}

// ---------------------------------------------------------------------------
// Fire Rules (tw_fire_code.py)
// ---------------------------------------------------------------------------

CheckResult ComplianceEngine::check_fire_construction(const nlohmann::json& plan) {
    static const char* ID   = "TW-FC-01";
    static const char* NAME = "防火構造";
    static const char* LAW  = "建築技術規則建築設計施工編 第69條";

    double height = building_height(plan);
    // >15m or >4F: must be fire-rated construction
    int n = num_stories(plan);
    if (height > 15.0 || n > 4)
        return make_info(ID, NAME, LAW,
            "高度 > 15m 或 4 層以上：需採防火構造（耐火時間依規定）",
            height, 15.0);

    return make_pass(ID, NAME, LAW,
        "建築高度 " + std::to_string(static_cast<int>(height)) + "m，防火構造規定確認",
        height, 15.0);
}

CheckResult ComplianceEngine::check_fire_compartment(const nlohmann::json& plan) {
    static const char* ID   = "TW-FC-02";
    static const char* NAME = "防火區劃";
    static const char* LAW  = "建築技術規則建築設計施工編 第79條";

    double total_area = total_floor_area(plan);
    if (total_area > 1500.0)
        return make_info(ID, NAME, LAW,
            "樓地板面積 > 1500㎡：需設防火區劃（每區 <= 1500㎡）",
            total_area, 1500.0);

    return make_pass(ID, NAME, LAW,
        "總樓地板面積符合防火區劃規定", total_area, 1500.0);
}

CheckResult ComplianceEngine::check_fire_escape(const nlohmann::json& plan) {
    static const char* ID   = "TW-FC-03";
    static const char* NAME = "安全梯設置";
    static const char* LAW  = "建築技術規則建築設計施工編 第95條";

    int n = num_stories(plan);
    if (n >= 11)
        return make_info(ID, NAME, LAW,
            "11 層以上：需設特別安全梯，直通頂樓", static_cast<double>(n), 11.0);

    if (n >= 6)
        return make_info(ID, NAME, LAW,
            "6 層以上：需設安全梯（防煙）", static_cast<double>(n), 6.0);

    return make_pass(ID, NAME, LAW,
        "樓層數符合安全梯規定", static_cast<double>(n), 5.0);
}

CheckResult ComplianceEngine::check_two_stairs(const nlohmann::json& plan) {
    static const char* ID   = "TW-FC-04";
    static const char* NAME = "雙向逃生";
    static const char* LAW  = "建築技術規則建築設計施工編 第96條";

    double total_area = total_floor_area(plan);
    int    n          = num_stories(plan);
    if (total_area > 240.0 && n >= 2)
        return make_info(ID, NAME, LAW,
            "2 層以上且總面積 > 240㎡：需設置 2 座以上樓梯",
            total_area, 240.0);

    return make_pass(ID, NAME, LAW,
        "雙向逃生規定確認", total_area, 240.0);
}

CheckResult ComplianceEngine::check_safety_stair(const nlohmann::json& plan) {
    static const char* ID   = "TW-FC-05";
    static const char* NAME = "安全梯寬度";
    static const char* LAW  = "建築技術規則建築設計施工編 第97條";

    int n = num_stories(plan);
    if (n >= 6)
        return make_info(ID, NAME, LAW,
            "6 層以上安全梯淨寬需 >= 1.2m，前室面積 >= 5㎡",
            static_cast<double>(n), 6.0);

    return make_pass(ID, NAME, LAW,
        "安全梯寬度規定確認", static_cast<double>(n), 5.0);
}

// ---------------------------------------------------------------------------
// Rule: Seismic Design — 耐震設計規範
// ---------------------------------------------------------------------------

CheckResult ComplianceEngine::check_seismic(const nlohmann::json& plan) {
    static const char* ID   = "TW-SD-01";
    static const char* NAME = "耐震設計";
    static const char* LAW  = "建築物耐震設計規範及解說";

    double height = building_height(plan);
    int    n      = num_stories(plan);

    if (height > 50.0 || n >= 16)
        return make_info(ID, NAME, LAW,
            "超高層（> 50m 或 16 層以上）：需進行特殊耐震分析",
            height, 50.0);

    return make_info(ID, NAME, LAW,
        "需依建築物耐震設計規範進行靜/動力分析，確認加速度係數",
        height, 50.0);
}

// ---------------------------------------------------------------------------
// Rule: Accessibility — 無障礙設施
// ---------------------------------------------------------------------------

CheckResult ComplianceEngine::check_accessibility(const nlohmann::json& plan) {
    static const char* ID   = "TW-ACC-01";
    static const char* NAME = "無障礙設施";
    static const char* LAW  = "建築技術規則建築設計施工編 第167條";

    int n = num_stories(plan);
    if (n >= 2)
        return make_info(ID, NAME, LAW,
            "2 層以上公共建築：需設置無障礙坡道、廁所、電梯",
            static_cast<double>(n), 2.0);

    return make_pass(ID, NAME, LAW,
        "無障礙設施規定確認", static_cast<double>(n), 2.0);
}

// ---------------------------------------------------------------------------
// Main: run all 15 rules
// ---------------------------------------------------------------------------

std::string ComplianceEngine::check(const std::string& plan_json,
                                     const std::string& land_json,
                                     const std::string& zoning_json) const
{
    nlohmann::json plan, land, zoning;
    try {
        plan   = nlohmann::json::parse(plan_json);
        land   = nlohmann::json::parse(land_json);
        zoning = nlohmann::json::parse(zoning_json);
    } catch (const nlohmann::json::exception& e) {
        nlohmann::json err = {{"error", std::string("JSON parse error: ") + e.what()}};
        return err.dump();
    }

    std::vector<CheckResult> results;
    results.push_back(check_bcr(plan, land, zoning));
    results.push_back(check_far(plan, land, zoning));
    results.push_back(check_height(plan, zoning));
    results.push_back(check_stairs(plan));
    results.push_back(check_corridor(plan));
    results.push_back(check_fire_construction(plan));
    results.push_back(check_fire_compartment(plan));
    results.push_back(check_fire_escape(plan));
    results.push_back(check_two_stairs(plan));
    results.push_back(check_safety_stair(plan));
    results.push_back(check_ceiling_height(plan));
    results.push_back(check_elevator(plan));
    results.push_back(check_parking(plan, land));
    results.push_back(check_seismic(plan));
    results.push_back(check_accessibility(plan));

    // Build summary
    int passed = 0, warnings = 0, failed = 0, info_count = 0;
    for (const auto& r : results) {
        switch (r.severity) {
            case Severity::PASS:    ++passed;    break;
            case Severity::WARNING: ++warnings;  break;
            case Severity::FAIL:    ++failed;    break;
            case Severity::INFO:    ++info_count; break;
        }
    }
    double rate = 0.0;
    if (passed + failed > 0)
        rate = std::round(static_cast<double>(passed) / (passed + failed) * 1000.0) / 10.0;

    nlohmann::json result_arr = nlohmann::json::array();
    for (const auto& r : results) result_arr.push_back(r.to_json());

    nlohmann::json out = {
        {"total_rules",      static_cast<int>(results.size())},
        {"passed",           passed},
        {"warnings",         warnings},
        {"failed",           failed},
        {"info",             info_count},
        {"compliance_rate",  rate},
        {"results",          result_arr},
    };
    return out.dump();
}

} // namespace promptbim

// ---------------------------------------------------------------------------
// C ABI
// ---------------------------------------------------------------------------

char* pb_check_compliance(const char* plan_json,
                          const char* land_json,
                          const char* zoning_json)
{
    if (!plan_json || !land_json || !zoning_json) return nullptr;
    try {
        promptbim::ComplianceEngine engine;
        std::string result = engine.check(plan_json, land_json, zoning_json);
        char* out = static_cast<char*>(std::malloc(result.size() + 1));
        if (!out) return nullptr;
        std::memcpy(out, result.data(), result.size() + 1);
        return out;
    } catch (...) {
        return nullptr;
    }
}

const char* pb_version(void) { return "2.5.0"; }

void pb_free_string(char* str) { std::free(str); }

// Placeholder stubs for Phase 3/4/5 (not yet implemented)
char* pb_estimate_cost(const char* plan_json);  // defined in cost_engine.cpp

// Phase 3/4 placeholders
PBPlan* pb_plan_from_json(const char*) { return nullptr; }
void    pb_plan_free(PBPlan*) {}
char*   pb_plan_to_json(const PBPlan*) { return nullptr; }
int     pb_generate_ifc(const PBPlan*, const char*) { return -1; }
int     pb_generate_usd(const PBPlan*, const char*) { return -1; }
int     pb_generate_usdz(const char*, const char*)  { return -1; }
PBLandParcel* pb_land_from_geojson(const char*)    { return nullptr; }
PBLandParcel* pb_land_from_shapefile(const char*)  { return nullptr; }
PBLandParcel* pb_land_from_dxf(const char*)        { return nullptr; }
void          pb_land_free(PBLandParcel*)           {}
char*         pb_land_to_json(const PBLandParcel*)  { return nullptr; }
char* pb_plan_mep(const char*, const char*)         { return nullptr; }
char* pb_generate_schedule(const char*, int)        { return nullptr; }
