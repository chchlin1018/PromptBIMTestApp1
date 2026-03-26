"""Tests for PDF cadastral document parser."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from promptbim.land.parsers.pdf_ocr import PDFLandParser, _shoelace_area, CADASTRAL_KEYWORDS


class TestShoelaceArea:
    def test_rectangle(self):
        coords = [(0, 0), (10, 0), (10, 5), (0, 5)]
        assert abs(_shoelace_area(coords) - 50.0) < 0.01

    def test_triangle(self):
        coords = [(0, 0), (10, 0), (5, 8)]
        assert abs(_shoelace_area(coords) - 40.0) < 0.01

    def test_empty(self):
        assert _shoelace_area([]) == 0.0

    def test_two_points(self):
        assert _shoelace_area([(0, 0), (1, 1)]) == 0.0


class TestPDFLandParser:
    def test_nonexistent_file(self):
        parser = PDFLandParser(use_ai=False)
        result = parser.parse("/nonexistent/file.pdf")
        assert result == []

    def test_is_cadastral_detection(self):
        parser = PDFLandParser(use_ai=False)
        assert parser._is_cadastral("地號: 123 面積: 500 平方公尺")
        assert parser._is_cadastral("cadastral map parcel boundary")
        assert not parser._is_cadastral("Hello world, this is a normal document")

    def test_parse_metadata_area(self):
        parser = PDFLandParser(use_ai=False)
        text = "土地資料\n面積: 1,234.56 平方公尺\n地號: 中山區 001-0023"
        metadata = parser._parse_metadata(text, [])
        assert abs(metadata["area_sqm"] - 1234.56) < 0.01
        assert "001-0023" in metadata["lot_number"]

    def test_parse_metadata_english(self):
        parser = PDFLandParser(use_ai=False)
        text = "Lot: ABC-123\nArea: 500 sqm\nAddress: 123 Main St"
        metadata = parser._parse_metadata(text, [])
        assert abs(metadata["area_sqm"] - 500.0) < 0.01
        assert metadata["lot_number"] == "ABC-123"
        assert metadata["address"] == "123 Main St"

    def test_extract_coords_from_tables(self):
        parser = PDFLandParser(use_ai=False)
        tables = [
            [
                ["Point", "X", "Y"],
                ["A", "0.0", "0.0"],
                ["B", "30.0", "0.0"],
                ["C", "30.0", "30.0"],
                ["D", "0.0", "30.0"],
            ]
        ]
        coords = parser._extract_coords_from_tables(tables)
        assert coords is not None
        assert len(coords) == 4
        assert coords[0] == (0.0, 0.0)

    def test_extract_coords_no_tables(self):
        parser = PDFLandParser(use_ai=False)
        assert parser._extract_coords_from_tables([]) is None

    def test_build_parcels_with_boundary(self):
        parser = PDFLandParser(use_ai=False)
        metadata = {"area_sqm": 900.0, "lot_number": "Test-001"}
        boundary = [(0, 0), (30, 0), (30, 30), (0, 30)]
        parcels = parser._build_parcels(metadata, boundary, Path("test.pdf"))
        assert len(parcels) == 1
        assert parcels[0].name == "Test-001"
        assert parcels[0].area_sqm == 900.0
        assert parcels[0].source_type == "pdf"

    def test_build_parcels_area_only(self):
        """If no boundary but area known, should create square approximation."""
        parser = PDFLandParser(use_ai=False)
        metadata = {"area_sqm": 400.0}
        parcels = parser._build_parcels(metadata, None, Path("test.pdf"))
        assert len(parcels) == 1
        assert abs(parcels[0].area_sqm - 400.0) < 1.0

    def test_build_parcels_nothing(self):
        parser = PDFLandParser(use_ai=False)
        parcels = parser._build_parcels({}, None, Path("test.pdf"))
        assert parcels == []

    @patch("promptbim.land.parsers.pdf_ocr.PDFLandParser._extract_text")
    @patch("promptbim.land.parsers.pdf_ocr.PDFLandParser._extract_tables")
    def test_parse_with_mocked_text(self, mock_tables, mock_text, tmp_path):
        """Full parse flow with mocked PDF text extraction."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake")  # just needs to exist

        mock_text.return_value = "地籍圖 土地資料\n地號: 大安-0001\n面積: 600.0 平方公尺"
        mock_tables.return_value = [
            [
                ["P", "X", "Y"],
                ["A", "0", "0"],
                ["B", "20", "0"],
                ["C", "20", "30"],
                ["D", "0", "30"],
            ]
        ]

        parser = PDFLandParser(use_ai=False)
        parcels = parser.parse(pdf_file)
        assert len(parcels) == 1
        assert parcels[0].source_type == "pdf"
        assert len(parcels[0].boundary) == 4
