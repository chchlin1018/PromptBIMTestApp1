"""KML/KMZ land parcel parser using fastkml."""

from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from shapely.geometry import Polygon

from promptbim.debug import get_logger
from promptbim.schemas.land import LandParcel

logger = get_logger("land.kml")

KML_NS = "{http://www.opengis.net/kml/2.2}"


def parse_kml(file_path: str | Path) -> list[LandParcel]:
    """Parse a KML or KMZ file and return list of LandParcel objects.

    Supports:
    - .kml files directly
    - .kmz files (ZIP containing doc.kml)
    """
    file_path = Path(file_path)

    from promptbim.land.parsers.utils import check_file_size

    check_file_size(file_path)

    if file_path.suffix.lower() == ".kmz":
        return _parse_kmz(file_path)

    kml_text = file_path.read_text(encoding="utf-8")
    return _parse_kml_string(kml_text, source_file=str(file_path))


def _parse_kmz(file_path: Path) -> list[LandParcel]:
    """Extract and parse KML from a KMZ (ZIP) file."""
    with zipfile.ZipFile(str(file_path), "r") as zf:
        kml_names = [n for n in zf.namelist() if n.lower().endswith(".kml")]
        if not kml_names:
            logger.warning("No KML file found in KMZ: %s", file_path)
            return []
        kml_text = zf.read(kml_names[0]).decode("utf-8")
    return _parse_kml_string(kml_text, source_file=str(file_path))


def _parse_kml_string(kml_text: str, source_file: str) -> list[LandParcel]:
    """Parse KML XML string into LandParcel objects using fastkml."""
    import fastkml

    root = ET.fromstring(kml_text)
    kml_obj = fastkml.KML.class_from_element(ns=KML_NS, element=root, strict=False)

    parcels: list[LandParcel] = []
    _extract_placemarks(kml_obj, parcels, source_file)
    return parcels


def _extract_placemarks(element, parcels: list[LandParcel], source_file: str) -> None:
    """Recursively extract Polygon placemarks from KML element tree."""
    features = list(getattr(element, "features", []))
    for feature in features:
        geom = getattr(feature, "geometry", None)
        if geom is not None:
            try:
                # fastkml returns pygeoif geometry; check type name instead of isinstance
                geom_type = type(geom).__name__
                if geom_type == "Polygon" and hasattr(geom, "exterior"):
                    coords = list(geom.exterior.coords[:-1])
                    coords_2d = [(c[0], c[1]) for c in coords]

                    # Compute area/perimeter via shapely for accuracy
                    shapely_poly = Polygon(coords_2d)

                    name = getattr(feature, "name", None) or f"Parcel {len(parcels) + 1}"
                    parcel = LandParcel(
                        name=name,
                        boundary=coords_2d,
                        area_sqm=shapely_poly.area,
                        perimeter_m=shapely_poly.length,
                        crs="EPSG:4326",
                        source_file=source_file,
                        source_type="kml",
                    )
                    parcels.append(parcel)
            except Exception as exc:
                logger.warning("Failed to parse KML geometry: %s", exc)

        # Recurse into sub-features (Folders, Documents)
        _extract_placemarks(feature, parcels, source_file)
