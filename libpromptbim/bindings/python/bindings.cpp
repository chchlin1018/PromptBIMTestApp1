/**
 * bindings.cpp — pybind11 Python bindings for libpromptbim
 *
 * Exposes compliance + cost + MEP + simulation engines to Python
 * for V1 backward compatibility.
 * Import as: from promptbim._native import check_compliance, estimate_cost, ...
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "promptbim/compliance_engine.hpp"
#include "promptbim/cost_engine.hpp"
#include "promptbim/mep_engine.hpp"
#include "promptbim/simulation_engine.hpp"
#include "promptbim/ifc_generator.hpp"
#include "promptbim/usd_generator.hpp"
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

    // -----------------------------------------------------------------------
    // MEP Engine
    // -----------------------------------------------------------------------
    py::class_<promptbim::MEPEngine>(m, "MEPEngine")
        .def(py::init<double>(), py::arg("grid_size") = 0.3)
        .def("plan_mep",
            &promptbim::MEPEngine::plan_mep,
            py::arg("plan_json"),
            py::arg("config_json") = "{}",
            "Generate MEP routes. Returns JSON string.");

    m.def("plan_mep",
        [](const std::string& plan_json, const std::string& config_json) {
            promptbim::MEPEngine engine;
            return engine.plan_mep(plan_json, config_json);
        },
        py::arg("plan_json"),
        py::arg("config_json") = "{}",
        "Plan MEP routes. Returns JSON string.");

    // -----------------------------------------------------------------------
    // Simulation Engine
    // -----------------------------------------------------------------------
    py::class_<promptbim::SimulationEngine>(m, "SimulationEngine")
        .def(py::init<>())
        .def("generate_schedule",
            &promptbim::SimulationEngine::generate_schedule_json,
            py::arg("plan_json"),
            py::arg("total_days") = 360,
            "Generate construction schedule. Returns JSON string.");

    m.def("generate_schedule",
        [](const std::string& plan_json, int total_days) {
            promptbim::SimulationEngine engine;
            return engine.generate_schedule_json(plan_json, total_days);
        },
        py::arg("plan_json"),
        py::arg("total_days") = 360,
        "Generate construction schedule. Returns JSON string.");

    // -----------------------------------------------------------------------
    // IFC Generator (Phase 3 — Sprint P20)
    // -----------------------------------------------------------------------
    py::class_<promptbim::IFCGenerator>(m, "IFCGenerator")
        .def(py::init<>())
        .def("generate",
            &promptbim::IFCGenerator::generate,
            py::arg("plan_json"),
            py::arg("output_path"),
            "Generate an IFC4 file. Returns 0 on success, -1 on error.")
        .def("generate_string",
            &promptbim::IFCGenerator::generate_string,
            py::arg("plan_json"),
            "Generate IFC content as a string.");

    m.def("generate_ifc",
        [](const std::string& plan_json, const std::string& output_path) {
            promptbim::IFCGenerator gen;
            return gen.generate(plan_json, output_path);
        },
        py::arg("plan_json"),
        py::arg("output_path"),
        "Generate IFC file. Returns 0 on success.");

    // -----------------------------------------------------------------------
    // USD Generator (Phase 3 — Sprint P20)
    // -----------------------------------------------------------------------
    py::class_<promptbim::USDGenerator>(m, "USDGenerator")
        .def(py::init<>())
        .def("generate",
            &promptbim::USDGenerator::generate,
            py::arg("plan_json"),
            py::arg("output_path"),
            "Generate a USDA file. Returns 0 on success, -1 on error.")
        .def("generate_string",
            &promptbim::USDGenerator::generate_string,
            py::arg("plan_json"),
            "Generate USDA content as a string.");

    m.def("generate_usd",
        [](const std::string& plan_json, const std::string& output_path) {
            promptbim::USDGenerator gen;
            return gen.generate(plan_json, output_path);
        },
        py::arg("plan_json"),
        py::arg("output_path"),
        "Generate USD file. Returns 0 on success.");

    // -----------------------------------------------------------------------
    // USDZ Packer (Phase 3 — Sprint P20)
    // -----------------------------------------------------------------------
    m.def("package_usdz",
        &promptbim::USDGenerator::package_usdz,
        py::arg("usd_path"),
        py::arg("output_path"),
        "Package USDA into USDZ. Returns 0 on success.");
}
