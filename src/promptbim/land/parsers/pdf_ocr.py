"""PDF cadastral document parser — extract land boundaries from PDF files.

Strategy:
1. Extract text/tables via pdfplumber for area, address, lot data
2. Extract embedded images via PyMuPDF (fitz) for boundary diagrams
3. If boundary image detected, delegate to Claude Vision (LandReaderAgent)
4. Combine text + boundary data into LandParcel
"""

from __future__ import annotations

import re
from pathlib import Path

from promptbim.bim.geometry import poly_area
from promptbim.debug import get_logger
from promptbim.schemas.land import LandParcel

logger = get_logger("land.pdf_ocr")

# Keywords that indicate a cadastral document (Chinese + English)
CADASTRAL_KEYWORDS = [
    "地號",
    "面積",
    "坐標",
    "座標",
    "地籍",
    "土地",
    "cadastral",
    "parcel",
    "lot",
    "boundary",
    "area",
]


class PDFLandParser:
    """Parse cadastral PDF documents to extract land boundaries."""

    def __init__(self, use_ai: bool = True):
        self._use_ai = use_ai

    def parse(self, pdf_path: str | Path) -> list[LandParcel]:
        """Extract land parcels from a PDF cadastral document.

        Returns a list of LandParcel objects. May be empty if no
        cadastral data is found.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            logger.warning("PDF file not found: %s", pdf_path)
            return []

        logger.info("Parsing PDF: %s", pdf_path.name)

        # Step 1: Extract text and tables
        text_data = self._extract_text(pdf_path)
        tables = self._extract_tables(pdf_path)

        # Step 2: Check if this looks like a cadastral document
        if not self._is_cadastral(text_data):
            logger.info("PDF does not appear to contain cadastral data")
            return []

        # Step 3: Parse area and metadata from text
        metadata = self._parse_metadata(text_data, tables)

        # Step 4: Try to extract boundary from embedded images
        boundary = None
        if self._use_ai:
            boundary = self._extract_boundary_from_images(pdf_path)

        # Step 5: Build LandParcel
        parcels = self._build_parcels(metadata, boundary, pdf_path)
        logger.info("Extracted %d parcel(s) from PDF", len(parcels))
        return parcels

    def _extract_text(self, pdf_path: Path) -> str:
        """Extract all text from PDF using pdfplumber."""
        try:
            import pdfplumber
        except ImportError:
            logger.warning("pdfplumber not installed; pip install pdfplumber")
            return ""

        text_parts = []
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text_parts.append(page_text)
                    logger.debug("Page %d: %d chars", page.page_number, len(page_text))
        except Exception as e:
            logger.error("Failed to extract text from PDF: %s", e)
            return ""

        return "\n".join(text_parts)

    def _extract_tables(self, pdf_path: Path) -> list[list[list[str]]]:
        """Extract tables from PDF using pdfplumber."""
        try:
            import pdfplumber
        except ImportError:
            return []

        all_tables = []
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables() or []
                    for table in tables:
                        # Clean None cells
                        cleaned = [[str(cell) if cell else "" for cell in row] for row in table]
                        all_tables.append(cleaned)
                    logger.debug("Page %d: %d tables", page.page_number, len(tables))
        except Exception as e:
            logger.error("Failed to extract tables: %s", e)

        return all_tables

    def _is_cadastral(self, text: str) -> bool:
        """Check if the text contains cadastral-related keywords."""
        text_lower = text.lower()
        matches = sum(1 for kw in CADASTRAL_KEYWORDS if kw in text_lower)
        is_match = matches >= 2
        logger.debug("Cadastral keyword matches: %d (threshold: 2)", matches)
        return is_match

    def _parse_metadata(self, text: str, tables: list) -> dict:
        """Extract area, lot number, address from text and tables."""
        metadata: dict = {}

        # Try to extract area (e.g., "面積: 123.45 平方公尺" or "area: 123.45 sqm")
        area_patterns = [
            r"面積[：:]\s*([\d,.]+)\s*(?:平方公尺|m²|sqm|㎡)",
            r"area[：:]\s*([\d,.]+)\s*(?:sqm|m²|square\s*met)",
            r"([\d,.]+)\s*(?:平方公尺|㎡)",
        ]
        for pattern in area_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                area_str = match.group(1).replace(",", "")
                try:
                    metadata["area_sqm"] = float(area_str)
                    logger.debug("Extracted area: %.2f sqm", metadata["area_sqm"])
                except ValueError:
                    pass
                break

        # Try to extract lot number (地號)
        lot_patterns = [
            r"地號[：:]\s*(.+?)(?:\n|$)",
            r"lot[：:\s]+(.+?)(?:\n|$)",
        ]
        for pattern in lot_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["lot_number"] = match.group(1).strip()
                logger.debug("Extracted lot number: %s", metadata["lot_number"])
                break

        # Try to extract address
        addr_patterns = [
            r"地址[：:]\s*(.+?)(?:\n|$)",
            r"address[：:\s]+(.+?)(?:\n|$)",
        ]
        for pattern in addr_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["address"] = match.group(1).strip()
                break

        # Try to extract coordinates from tables
        coords = self._extract_coords_from_tables(tables)
        if coords:
            metadata["boundary"] = coords

        return metadata

    def _extract_coords_from_tables(self, tables: list) -> list[tuple[float, float]] | None:
        """Try to extract coordinate pairs from table data."""
        for table in tables:
            coords = []
            for row in table:
                # Look for rows with 2 numeric columns (x, y)
                nums = []
                for cell in row:
                    cell_clean = cell.strip().replace(",", "")
                    try:
                        nums.append(float(cell_clean))
                    except ValueError:
                        continue
                if len(nums) >= 2:
                    coords.append((nums[0], nums[1]))

            if len(coords) >= 3:
                logger.debug("Found %d coordinate pairs in table", len(coords))
                return coords

        return None

    def _extract_boundary_from_images(self, pdf_path: Path) -> list[tuple[float, float]] | None:
        """Extract images from PDF and use AI to identify boundaries."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.debug("PyMuPDF not installed; skipping image extraction")
            return None

        try:
            doc = fitz.open(str(pdf_path))
            for page_num, page in enumerate(doc):
                images = page.get_images(full=True)
                if not images:
                    continue

                logger.debug("Page %d has %d images", page_num + 1, len(images))

                # Extract largest image (most likely the cadastral map)
                largest_img = None
                largest_size = 0
                for img_info in images:
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    if base_image and len(base_image["image"]) > largest_size:
                        largest_size = len(base_image["image"])
                        largest_img = base_image

                if largest_img and largest_size > 5000:
                    logger.info(
                        "Extracted image: %d bytes, format=%s",
                        largest_size,
                        largest_img.get("ext", "unknown"),
                    )
                    return self._ai_recognize_boundary(largest_img["image"])

            doc.close()
        except Exception as e:
            logger.error("Image extraction failed: %s", e)

        return None

    def _ai_recognize_boundary(self, image_data: bytes) -> list[tuple[float, float]] | None:
        """Use Claude Vision to recognize boundary from image."""
        import base64

        try:
            from promptbim.agents.land_reader import LandReaderAgent

            b64 = base64.b64encode(image_data).decode("utf-8")
            agent = LandReaderAgent()
            result = agent.recognize_from_b64(b64, media_type="image/png")
            if result and result.get("boundary"):
                boundary = [(p[0], p[1]) for p in result["boundary"]]
                if len(boundary) >= 3:
                    logger.info("AI recognized %d boundary points", len(boundary))
                    return boundary
        except Exception as e:
            logger.warning("AI boundary recognition failed: %s", e)

        return None

    def _build_parcels(
        self,
        metadata: dict,
        boundary: list[tuple[float, float]] | None,
        pdf_path: Path,
    ) -> list[LandParcel]:
        """Build LandParcel objects from extracted data."""
        # Use extracted boundary or table coordinates
        coords = boundary or metadata.get("boundary")
        if not coords:
            # Fallback: if we have area, create a square approximation
            area = metadata.get("area_sqm")
            if area and area > 0:
                import math

                side = math.sqrt(area)
                coords = [(0, 0), (side, 0), (side, side), (0, side)]
                logger.info("No boundary found; approximating as %.1fm square", side)
            else:
                logger.warning("No boundary or area data found in PDF")
                return []

        # Calculate area from boundary if not in metadata
        area = metadata.get("area_sqm", 0.0)
        if area <= 0 and coords:
            area = poly_area(coords)

        name = metadata.get("lot_number", pdf_path.stem)

        parcel = LandParcel(
            name=name,
            boundary=coords,
            area_sqm=area,
            source_file=str(pdf_path),
            source_type="pdf",
            ai_annotations={k: v for k, v in metadata.items() if k not in ("boundary", "area_sqm")}
            or None,
        )
        return [parcel]
