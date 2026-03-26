/**
 * pb_plan_internal.h — Internal PBPlan struct definition
 *
 * Shared between ifc_generator.cpp and usd_generator.cpp.
 * Not part of public API — only used for C ABI implementation.
 */

#pragma once

#include <string>

struct PBPlan {
    std::string json_data;
};
