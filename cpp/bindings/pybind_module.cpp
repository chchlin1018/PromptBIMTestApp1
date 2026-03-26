// PromptBIM C++ Core — pybind11 Python Bindings
// Usage: import promptbim_cpp

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "compliance_engine.h"
#include "cost_engine.h"

namespace py = pybind11;

PYBIND11_MODULE(promptbim_cpp, m) {
    m.doc() = "PromptBIM C++ Core — Compliance + Cost Engines";

    // === ComplianceEngine ===
    py::class_<promptbim::ZoningParams>(m, "ZoningParams")
        .def(py::init<>())
        .def_readwrite("zone_type", &promptbim::ZoningParams::zone_type)
        .def_readwrite("bcr_limit", &promptbim::ZoningParams::bcr_limit)
        .def_readwrite("far_limit", &promptbim::ZoningParams::far_limit)
        .def_readwrite("height_limit_m", &promptbim::ZoningParams::height_limit_m)
        .def_readwrite("setback_front_m", &promptbim::ZoningParams::setback_front_m)
        .def_readwrite("setback_back_m", &promptbim::ZoningParams::setback_back_m)
        .def_readwrite("setback_left_m", &promptbim::ZoningParams::setback_left_m)
        .def_readwrite("setback_right_m", &promptbim::ZoningParams::setback_right_m);

    py::class_<promptbim::ComplianceResult>(m, "ComplianceResult")
        .def(py::init<>())
        .def_readonly("passed", &promptbim::ComplianceResult::passed)
        .def_readonly("bcr", &promptbim::ComplianceResult::bcr)
        .def_readonly("far_ratio", &promptbim::ComplianceResult::far_ratio)
        .def_readonly("height_m", &promptbim::ComplianceResult::height_m)
        .def_readonly("violations", &promptbim::ComplianceResult::violations)
        .def_readonly("warnings", &promptbim::ComplianceResult::warnings);

    py::class_<promptbim::ComplianceEngine>(m, "ComplianceEngine")
        .def(py::init<>())
        .def("check", &promptbim::ComplianceEngine::check,
             py::arg("land_area_sqm"),
             py::arg("building_footprint_sqm"),
             py::arg("total_floor_area_sqm"),
             py::arg("building_height_m"),
             py::arg("zoning"))
        .def_static("version", &promptbim::ComplianceEngine::version);

    // === CostEngine ===
    py::class_<promptbim::BuildingParams>(m, "BuildingParams")
        .def(py::init<>())
        .def_readwrite("total_floor_area_sqm", &promptbim::BuildingParams::total_floor_area_sqm)
        .def_readwrite("num_stories", &promptbim::BuildingParams::num_stories)
        .def_readwrite("building_type", &promptbim::BuildingParams::building_type)
        .def_readwrite("structure_type", &promptbim::BuildingParams::structure_type)
        .def_readwrite("quality_level", &promptbim::BuildingParams::quality_level);

    py::class_<promptbim::CostBreakdown>(m, "CostBreakdown")
        .def(py::init<>())
        .def_readonly("structure_cost", &promptbim::CostBreakdown::structure_cost)
        .def_readonly("exterior_cost", &promptbim::CostBreakdown::exterior_cost)
        .def_readonly("interior_cost", &promptbim::CostBreakdown::interior_cost)
        .def_readonly("mep_cost", &promptbim::CostBreakdown::mep_cost)
        .def_readonly("total_cost", &promptbim::CostBreakdown::total_cost)
        .def_readonly("cost_per_sqm", &promptbim::CostBreakdown::cost_per_sqm)
        .def_readonly("currency", &promptbim::CostBreakdown::currency);

    py::class_<promptbim::CostEngine>(m, "CostEngine")
        .def(py::init<>())
        .def("estimate", &promptbim::CostEngine::estimate,
             py::arg("params"))
        .def_static("version", &promptbim::CostEngine::version);
}
