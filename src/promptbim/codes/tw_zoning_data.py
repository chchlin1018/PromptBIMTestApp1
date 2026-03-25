"""Taiwan zoning BCR/FAR data for major cities and non-urban land."""

from __future__ import annotations

# -- Urban zoning by city --------------------------------------------------

TAIPEI_ZONING: dict[str, dict[str, float]] = {
    "住一": {"bcr": 0.30, "far": 0.60},
    "住二": {"bcr": 0.35, "far": 1.20},
    "住三": {"bcr": 0.45, "far": 2.25},
    "住三之一": {"bcr": 0.45, "far": 1.60},
    "住三之二": {"bcr": 0.50, "far": 3.00},
    "住四": {"bcr": 0.50, "far": 3.00},
    "住四之一": {"bcr": 0.50, "far": 2.00},
    "商一": {"bcr": 0.55, "far": 3.60},
    "商二": {"bcr": 0.65, "far": 6.30},
    "商三": {"bcr": 0.65, "far": 5.60},
    "商四": {"bcr": 0.75, "far": 8.00},
    "工二": {"bcr": 0.55, "far": 2.10},
    "工三": {"bcr": 0.60, "far": 3.00},
}

NEW_TAIPEI_ZONING: dict[str, dict[str, float]] = {
    "住一": {"bcr": 0.30, "far": 0.60},
    "住二": {"bcr": 0.40, "far": 1.50},
    "住三": {"bcr": 0.50, "far": 2.40},
    "住四": {"bcr": 0.50, "far": 3.00},
    "商一": {"bcr": 0.60, "far": 3.60},
    "商二": {"bcr": 0.70, "far": 6.30},
    "商三": {"bcr": 0.70, "far": 5.60},
    "工二": {"bcr": 0.55, "far": 2.10},
    "工三": {"bcr": 0.60, "far": 3.00},
}

TAOYUAN_ZONING: dict[str, dict[str, float]] = {
    "住一": {"bcr": 0.30, "far": 0.60},
    "住二": {"bcr": 0.40, "far": 1.50},
    "住三": {"bcr": 0.50, "far": 2.40},
    "住四": {"bcr": 0.50, "far": 3.00},
    "商一": {"bcr": 0.60, "far": 3.60},
    "商二": {"bcr": 0.70, "far": 6.30},
    "工二": {"bcr": 0.55, "far": 2.10},
    "工三": {"bcr": 0.60, "far": 3.00},
}

TAICHUNG_ZONING: dict[str, dict[str, float]] = {
    "住一": {"bcr": 0.30, "far": 0.60},
    "住二": {"bcr": 0.40, "far": 1.60},
    "住三": {"bcr": 0.50, "far": 2.40},
    "住四": {"bcr": 0.50, "far": 3.00},
    "商一": {"bcr": 0.60, "far": 3.60},
    "商二": {"bcr": 0.70, "far": 6.30},
    "商三": {"bcr": 0.70, "far": 5.60},
    "工二": {"bcr": 0.55, "far": 2.10},
    "工三": {"bcr": 0.60, "far": 3.00},
}

TAINAN_ZONING: dict[str, dict[str, float]] = {
    "住一": {"bcr": 0.30, "far": 0.60},
    "住二": {"bcr": 0.40, "far": 1.50},
    "住三": {"bcr": 0.50, "far": 2.40},
    "住四": {"bcr": 0.50, "far": 3.00},
    "商一": {"bcr": 0.60, "far": 3.60},
    "商二": {"bcr": 0.70, "far": 6.30},
    "工二": {"bcr": 0.55, "far": 2.10},
    "工三": {"bcr": 0.60, "far": 3.00},
}

KAOHSIUNG_ZONING: dict[str, dict[str, float]] = {
    "住一": {"bcr": 0.30, "far": 0.60},
    "住二": {"bcr": 0.40, "far": 1.50},
    "住三": {"bcr": 0.50, "far": 2.40},
    "住四": {"bcr": 0.50, "far": 3.00},
    "商一": {"bcr": 0.60, "far": 3.60},
    "商二": {"bcr": 0.70, "far": 6.30},
    "商三": {"bcr": 0.70, "far": 5.60},
    "工二": {"bcr": 0.55, "far": 2.10},
    "工三": {"bcr": 0.60, "far": 3.00},
}

# Map city names to their zoning tables
CITY_ZONING: dict[str, dict[str, dict[str, float]]] = {
    "台北市": TAIPEI_ZONING,
    "新北市": NEW_TAIPEI_ZONING,
    "桃園市": TAOYUAN_ZONING,
    "台中市": TAICHUNG_ZONING,
    "台南市": TAINAN_ZONING,
    "高雄市": KAOHSIUNG_ZONING,
}

# -- Non-urban land --------------------------------------------------------

NON_URBAN_ZONING: dict[str, dict[str, float]] = {
    "甲種建築用地": {"bcr": 0.60, "far": 2.40},
    "乙種建築用地": {"bcr": 0.60, "far": 2.40},
    "丙種建築用地": {"bcr": 0.40, "far": 1.20},
    "丁種建築用地": {"bcr": 0.70, "far": 3.00},
}

# -- Generic zone type mapping (fallback) -----------------------------------

GENERIC_ZONE_DEFAULTS: dict[str, dict[str, float]] = {
    "residential": {"bcr": 0.50, "far": 2.40},
    "commercial": {"bcr": 0.65, "far": 5.60},
    "industrial": {"bcr": 0.60, "far": 3.00},
}


def lookup_zoning(
    city: str = "",
    zone_name: str = "",
    zone_type: str = "residential",
) -> dict[str, float]:
    """Look up BCR/FAR limits.

    Tries city-specific table first, falls back to non-urban, then generic.
    """
    if city and zone_name:
        city_table = CITY_ZONING.get(city)
        if city_table and zone_name in city_table:
            return city_table[zone_name]

    if zone_name in NON_URBAN_ZONING:
        return NON_URBAN_ZONING[zone_name]

    return GENERIC_ZONE_DEFAULTS.get(zone_type, GENERIC_ZONE_DEFAULTS["residential"])
