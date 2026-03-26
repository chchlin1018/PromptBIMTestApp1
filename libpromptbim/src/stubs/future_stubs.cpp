/**
 * future_stubs.cpp — Placeholder stubs for Phase 4/5 (not yet implemented)
 *
 * Phase 3 BIM Engine stubs have been replaced by real implementations:
 *   - src/bim/ifc_generator.cpp (PBPlan, pb_generate_ifc)
 *   - src/bim/usd_generator.cpp (pb_generate_usd, pb_generate_usdz)
 *
 * These stubs provide valid C ABI symbols so the shared library links correctly
 * even before Phase 4/5 modules are implemented.
 */

#include "promptbim/promptbim.h"

#include <cstdlib>
#include <cstring>

// -----------------------------------------------------------------------
// Phase 4: GIS Engine placeholders
// -----------------------------------------------------------------------

PBLandParcel* pb_land_from_geojson(const char*)    { return nullptr; }
PBLandParcel* pb_land_from_shapefile(const char*)  { return nullptr; }
PBLandParcel* pb_land_from_dxf(const char*)        { return nullptr; }
void          pb_land_free(PBLandParcel*)           {}
char*         pb_land_to_json(const PBLandParcel*)  { return nullptr; }
