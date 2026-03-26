/**
 * future_stubs.cpp — Placeholder stubs for Phase 3/4/5 (not yet implemented)
 *
 * Separated from compliance_engine.cpp (P18 tech debt).
 * These stubs provide valid C ABI symbols so the shared library links correctly
 * even before Phase 3/4/5 modules are implemented.
 */

#include "promptbim/promptbim.h"

#include <cstdlib>
#include <cstring>

// -----------------------------------------------------------------------
// Phase 3: BIM Engine placeholders
// -----------------------------------------------------------------------

PBPlan* pb_plan_from_json(const char*) { return nullptr; }
void    pb_plan_free(PBPlan*) {}
char*   pb_plan_to_json(const PBPlan*) { return nullptr; }

int pb_generate_ifc(const PBPlan*, const char*) { return -1; }
int pb_generate_usd(const PBPlan*, const char*) { return -1; }
int pb_generate_usdz(const char*, const char*)  { return -1; }

// -----------------------------------------------------------------------
// Phase 4: GIS Engine placeholders
// -----------------------------------------------------------------------

PBLandParcel* pb_land_from_geojson(const char*)    { return nullptr; }
PBLandParcel* pb_land_from_shapefile(const char*)  { return nullptr; }
PBLandParcel* pb_land_from_dxf(const char*)        { return nullptr; }
void          pb_land_free(PBLandParcel*)           {}
char*         pb_land_to_json(const PBLandParcel*)  { return nullptr; }
