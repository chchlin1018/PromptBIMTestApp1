"""Tests for KML/KMZ land parcel parser."""

from pathlib import Path

import pytest

from promptbim.land.parsers.kml import parse_kml

SAMPLE_KML = """\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Test Parcels</name>
    <Placemark>
      <name>Test Parcel A</name>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              121.5,25.0,0
              121.501,25.0,0
              121.501,25.001,0
              121.5,25.001,0
              121.5,25.0,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
    <Placemark>
      <name>Test Parcel B</name>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              121.51,25.01,0
              121.512,25.01,0
              121.512,25.012,0
              121.51,25.012,0
              121.51,25.01,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>
"""


@pytest.fixture
def kml_file(tmp_path: Path) -> Path:
    """Create a temporary KML file."""
    p = tmp_path / "test.kml"
    p.write_text(SAMPLE_KML, encoding="utf-8")
    return p


def test_parse_kml_returns_parcels(kml_file: Path):
    parcels = parse_kml(kml_file)
    assert len(parcels) == 2


def test_parse_kml_parcel_names(kml_file: Path):
    parcels = parse_kml(kml_file)
    assert parcels[0].name == "Test Parcel A"
    assert parcels[1].name == "Test Parcel B"


def test_parse_kml_source_type(kml_file: Path):
    parcels = parse_kml(kml_file)
    for p in parcels:
        assert p.source_type == "kml"
        assert p.crs == "EPSG:4326"


def test_parse_kml_boundary_coords(kml_file: Path):
    parcels = parse_kml(kml_file)
    # First parcel boundary should have 4 vertices
    assert len(parcels[0].boundary) == 4
    # Check first coordinate approximately (lon, lat)
    assert abs(parcels[0].boundary[0][0] - 121.5) < 0.01
    assert abs(parcels[0].boundary[0][1] - 25.0) < 0.01


def test_parse_kml_area_positive(kml_file: Path):
    parcels = parse_kml(kml_file)
    for p in parcels:
        assert p.area_sqm > 0


def test_parse_kmz(tmp_path: Path):
    """Test parsing KMZ (ZIP-wrapped KML)."""
    import zipfile

    kml_path = tmp_path / "doc.kml"
    kml_path.write_text(SAMPLE_KML, encoding="utf-8")

    kmz_path = tmp_path / "test.kmz"
    with zipfile.ZipFile(str(kmz_path), "w") as zf:
        zf.write(str(kml_path), "doc.kml")

    parcels = parse_kml(kmz_path)
    assert len(parcels) == 2


def test_parse_kml_empty_file(tmp_path: Path):
    """Empty KML should return empty list."""
    p = tmp_path / "empty.kml"
    p.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<kml xmlns="http://www.opengis.net/kml/2.2"><Document></Document></kml>',
        encoding="utf-8",
    )
    parcels = parse_kml(p)
    assert parcels == []


def test_parse_kml_with_folder_nesting(tmp_path: Path):
    """KML with nested Folders should still extract Placemarks."""
    kml_text = """\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Folder>
      <name>My Folder</name>
      <Placemark>
        <name>Nested Parcel</name>
        <Polygon>
          <outerBoundaryIs>
            <LinearRing>
              <coordinates>
                121.5,25.0,0 121.502,25.0,0 121.502,25.002,0 121.5,25.002,0 121.5,25.0,0
              </coordinates>
            </LinearRing>
          </outerBoundaryIs>
        </Polygon>
      </Placemark>
    </Folder>
  </Document>
</kml>
"""
    p = tmp_path / "nested.kml"
    p.write_text(kml_text, encoding="utf-8")
    parcels = parse_kml(p)
    assert len(parcels) == 1
    assert parcels[0].name == "Nested Parcel"
