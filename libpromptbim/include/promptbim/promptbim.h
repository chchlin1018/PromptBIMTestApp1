/**
 * promptbim.h — Public C ABI for libpromptbim
 *
 * This header defines the stable C ABI used by:
 *   - Swift via C interop (macOS SwiftUI app)
 *   - Python via pybind11 / ctypes
 *   - WebAssembly via Emscripten
 *   - Windows Qt 6 via FFI
 *
 * All strings are UTF-8 encoded.
 * Caller must free strings returned by pb_*() functions using pb_free_string().
 * Caller must free opaque structs using the corresponding pb_*_free() function.
 *
 * Version: 2.11.0
 */

#pragma once

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>

/* =========================================================================
 * Version
 * ========================================================================= */

/** Returns "2.11.0" — owned by the library, do NOT free. */
const char* pb_version(void);

/* =========================================================================
 * Memory management
 * ========================================================================= */

/** Free a JSON string returned by any pb_*_to_json() function. */
void pb_free_string(char* str);

/* =========================================================================
 * Compliance Engine
 * =========================================================================
 *
 * Input (JSON):
 *   plan    — BuildingPlan JSON (see schemas/plan.json)
 *   land    — LandParcel JSON  (area_sqm, footprint)
 *   zoning  — ZoningInfo JSON  (bcr_limit, far_limit, height_limit_m, ...)
 *
 * Output (JSON):
 *   {
 *     "total_rules": N,
 *     "passed": N, "warnings": N, "failed": N, "info": N,
 *     "compliance_rate": 95.0,
 *     "results": [
 *       {
 *         "rule_id": "TW-BTC-BCR",
 *         "rule_name": "建蔽率檢查",
 *         "law_reference": "建築技術規則建築設計施工編 第25條",
 *         "severity": "pass"|"warning"|"fail"|"info",
 *         "message": "...",
 *         "actual_value": 0.42,
 *         "limit_value": 0.60,
 *         "suggestion": "..."
 *       }, ...
 *     ]
 *   }
 *
 * Returns: JSON string (caller must free with pb_free_string).
 *          NULL on error.
 */
char* pb_check_compliance(
    const char* plan_json,
    const char* land_json,
    const char* zoning_json
);

/* =========================================================================
 * Cost Engine
 * =========================================================================
 *
 * Input (JSON): BuildingPlan JSON
 *
 * Output (JSON):
 *   {
 *     "project": "...",
 *     "total_cost_twd": 12345678,
 *     "total_floor_area_sqm": 1234.5,
 *     "cost_per_sqm_twd": 45678,
 *     "breakdown": [
 *       { "category": "結構工程", "cost": 3456789, "ratio": 0.28 }, ...
 *     ],
 *     "notes": "POC-grade estimate (+-30%)"
 *   }
 *
 * Returns: JSON string (caller must free with pb_free_string).
 *          NULL on error.
 */
char* pb_estimate_cost(const char* plan_json);

/* =========================================================================
 * BIM Engine (Phase 3 — IMPLEMENTED, Sprint P20)
 * =========================================================================
 *
 * IFC Generator: writes IFC4 SPF (STEP Physical File) directly in C++.
 * USD Generator: writes USDA (ASCII) files directly in C++.
 * USDZ Packer:  packages USDA into uncompressed zip archive per spec.
 *
 * PBPlan lifecycle:
 *   1. pb_plan_from_json(json) → allocates PBPlan*
 *   2. pb_generate_ifc/usd(plan, path) → writes file
 *   3. pb_plan_free(plan) → deallocates
 */

typedef struct PBPlan PBPlan;

PBPlan* pb_plan_from_json(const char* json_str);
void    pb_plan_free(PBPlan* plan);
char*   pb_plan_to_json(const PBPlan* plan);

int pb_generate_ifc(const PBPlan* plan, const char* output_path);
int pb_generate_usd(const PBPlan* plan, const char* output_path);
int pb_generate_usdz(const char* usd_path, const char* output_path);

/* =========================================================================
 * GIS Engine (Phase 4 — IMPLEMENTED, Sprint P21)
 * =========================================================================
 *
 * Land parcel parsing from GeoJSON, Shapefile, DXF.
 * Geometry operations: setback/buffer, area, centroid, perimeter.
 * Coordinate projection: WGS84 ↔ TWD97 TM2 (EPSG:3826).
 *
 * PBLandParcel lifecycle:
 *   1. pb_land_from_*(path) → allocates PBLandParcel*
 *   2. pb_land_to_json(parcel) → JSON string (caller frees with pb_free_string)
 *   3. pb_land_free(parcel) → deallocates
 */

typedef struct PBLandParcel PBLandParcel;

PBLandParcel* pb_land_from_geojson(const char* path);
PBLandParcel* pb_land_from_shapefile(const char* path);
PBLandParcel* pb_land_from_dxf(const char* path);
void          pb_land_free(PBLandParcel* parcel);
char*         pb_land_to_json(const PBLandParcel* parcel);

/** Parse GeoJSON string (not file) into LandParcel. */
PBLandParcel* pb_land_from_geojson_string(const char* geojson_str);

/* =========================================================================
 * MEP Engine (Phase 2 — placeholder)
 * ========================================================================= */

char* pb_plan_mep(const char* plan_json, const char* config_json);

/* =========================================================================
 * Simulation Engine (Phase 2 — placeholder)
 * ========================================================================= */

char* pb_generate_schedule(const char* plan_json, int total_days);

#ifdef __cplusplus
}
#endif
