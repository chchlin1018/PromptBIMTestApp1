/**
 * bindings.cpp — pybind11 Python bindings for libpromptbim
 *
 * Exposes compliance + cost engines to Python for V1 backward compatibility.
 * Import as: from promptbim._native import check_compliance, estimate_cost
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "promptbim/compliance_engine.hpp"
#include "promptbim/cost_engine.hpp"
#include "promptbim/promptbim.h"

namespace py = pybind11;

PYBIND11_MODULE(_native, m) {
    m.doc() = "PromptBIM native C++ engines (pybind11)";

    m.attr("__version__") = pb_version();

    // -----------------------------------------------------------------------
    // Compliance Engine
    // -----------------------------------------------------------------------
    py::class_<promptbim::ComplianceEngine>(m, "ComplianceEngine")
        .def(py::init<>())
        .def("check",
            &promptbim::ComplianceEngine::check,
            py::arg("plan_json"),
            py::arg("land_json"),
            py::arg("zoning_json"),
            R"doc(
Run all 15 Taiwan building code rules.

Args:
    plan_json:   BuildingPlan serialized to JSON string
    land_json:   LandParcel   serialized to JSON string
    zoning_json: ZoningInfo   serialized to JSON string

Returns:
    JSON string with compliance summary and per-rule results.
            )doc");

    // Convenience free function (mirrors Python API)
    m.def("check_compliance",
        [](const std::string& plan_json,
           const std::string& land_json,
           const std::string& zoning_json) {
            promptbim::ComplianceEngine engine;
            return engine.check(plan_json, land_json, zoning_json);
        },
        py::arg("plan_json"),
        py::arg("land_json"),
        py::arg("zoning_json"),
        "Run compliance check. Returns JSON string.");

    // -----------------------------------------------------------------------
    // Cost Engine
    // -----------------------------------------------------------------------
    py::class_<promptbim::CostEngine>(m, "CostEngine")
        .def(py::init<>())
        .def("estimate",
            &promptbim::CostEngine::estimate,
            py::arg("plan_json"),
            R"doc(
Estimate construction cost from a BuildingPlan JSON.

Args:
    plan_json: BuildingPlan serialized to JSON string

Returns:
    JSON string with CostEstimate (total, per-sqm, breakdown).
            )doc");

    m.def("estimate_cost",
        [](const std::string& plan_json) {
            promptbim::CostEngine engine;
            return engine.estimate(plan_json);
        },
        py::arg("plan_json"),
        "Estimate cost. Returns JSON string.");
}
