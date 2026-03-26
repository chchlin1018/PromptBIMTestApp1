/**
 * cost_engine.hpp — Construction Cost Estimation Engine (C++)
 *
 * Ports src/promptbim/bim/cost/ (QTO + estimator + unit prices) to native C++.
 */

#pragma once

#include <string>
#include <nlohmann/json.hpp>

namespace promptbim {

class CostEngine {
public:
    /**
     * Estimate construction cost from a BuildingPlan JSON.
     *
     * @param plan_json  BuildingPlan as JSON string
     * @return           CostEstimate as JSON string
     */
    std::string estimate(const std::string& plan_json) const;

private:
    struct QTOItem {
        std::string category;
        std::string name;
        double      quantity = 0.0;
        std::string unit;
        std::string story;
    };

    struct CostLineItem {
        std::string category;
        std::string name;
        double      quantity      = 0.0;
        std::string unit;
        double      unit_price    = 0.0;
        double      total         = 0.0;
        std::string price_key;
    };

    std::vector<QTOItem>      extract_qto(const nlohmann::json& plan) const;
    std::vector<CostLineItem> price_items(const std::vector<QTOItem>& items) const;
    std::vector<CostLineItem> interior_finish_allowance(const std::vector<QTOItem>& items) const;
};

} // namespace promptbim
