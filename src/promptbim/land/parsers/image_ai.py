"""AI-powered land image parser using Claude Vision.

Accepts arbitrary image files (photos, screenshots, scanned maps, sketches)
and uses the LandReaderAgent to extract land boundary polygons.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from promptbim.debug import get_logger
from promptbim.land.parsers.image_preprocess import (
    is_supported_image,
    prepare_for_vision_api,
)
from promptbim.schemas.land import LandParcel

logger = get_logger("land.image_ai")


@dataclass
class AIRecognitionResult:
    """Result of AI land image recognition."""

    parcels: list[LandParcel] = field(default_factory=list)
    raw_response: dict | None = None
    confidence: float = 0.0
    notes: str = ""
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and len(self.parcels) > 0


def parse_image_ai(
    file_path: str | Path,
    context: str | None = None,
) -> AIRecognitionResult:
    """Parse a land image using Claude Vision AI.

    Args:
        file_path: Path to image file (JPG, PNG, TIFF, BMP, WebP, HEIC, PDF).
        context: Optional context string for the AI (location, expected size).

    Returns:
        AIRecognitionResult with extracted LandParcel(s).
    """
    path = Path(file_path)
    logger.debug("parse_image_ai: file=%s, context=%s", path, context)

    if not path.exists():
        return AIRecognitionResult(error=f"File not found: {path}")

    if not is_supported_image(path):
        return AIRecognitionResult(error=f"Unsupported image format: {path.suffix}")

    try:
        b64_data, media_type = prepare_for_vision_api(path)
        logger.debug("Image preprocessed: base64_size=%d bytes, media_type=%s", len(b64_data), media_type)
    except Exception as exc:
        return AIRecognitionResult(error=f"Image preprocessing failed: {exc}")

    try:
        import time as _time
        from promptbim.agents.land_reader import LandReaderAgent

        agent = LandReaderAgent()
        _t0 = _time.time()
        response = agent.analyse_image(b64_data, media_type, context=context)
        _elapsed = _time.time() - _t0
        logger.debug("AI response: %.2fs, ok=%s", _elapsed, response.ok)
    except Exception as exc:
        return AIRecognitionResult(error=f"AI agent error: {exc}")

    if not response.ok:
        return AIRecognitionResult(error=f"AI analysis failed: {response.error}")

    if not response.json_data:
        return AIRecognitionResult(
            error="AI returned no structured data",
            notes=response.text,
        )

    result = _build_result(response.json_data, path)
    logger.debug("Recognition result: confidence=%.2f, parcels=%d", result.confidence, len(result.parcels))
    return result


def parse_image_ai_from_b64(
    b64_data: str,
    media_type: str = "image/jpeg",
    source_name: str = "ai_image",
    context: str | None = None,
) -> AIRecognitionResult:
    """Parse from pre-encoded base64 image data (for testing/API use)."""
    try:
        from promptbim.agents.land_reader import LandReaderAgent

        agent = LandReaderAgent()
        response = agent.analyse_image(b64_data, media_type, context=context)
    except Exception as exc:
        return AIRecognitionResult(error=f"AI agent error: {exc}")

    if not response.ok:
        return AIRecognitionResult(error=f"AI analysis failed: {response.error}")

    if not response.json_data:
        return AIRecognitionResult(error="AI returned no structured data", notes=response.text)

    return _build_result(response.json_data, Path(source_name))


def build_parcel_from_ai_data(
    data: dict,
    source_path: Path | None = None,
) -> LandParcel | None:
    """Build a LandParcel from AI recognition JSON data.

    This is also used by tests and the boundary confirmation flow.
    """
    boundary_raw = data.get("boundary")
    if not boundary_raw or len(boundary_raw) < 3:
        return None

    boundary = [(float(pt[0]), float(pt[1])) for pt in boundary_raw]

    area = data.get("area_sqm")
    if area is None:
        area = _shoelace_area(boundary)

    perimeter = _polygon_perimeter(boundary)

    annotations = data.get("annotations", {}) or {}
    name = annotations.get("lot_number") or annotations.get("address") or "AI-Recognized Parcel"

    return LandParcel(
        name=name,
        boundary=boundary,
        area_sqm=float(area),
        perimeter_m=perimeter,
        crs="LOCAL",
        source_file=str(source_path) if source_path else None,
        source_type="ai_image",
        ai_confidence=float(data.get("confidence", 0.5)),
        original_image_path=str(source_path) if source_path else None,
        ai_annotations=annotations,
    )


def _build_result(data: dict, source_path: Path) -> AIRecognitionResult:
    """Build AIRecognitionResult from parsed AI JSON response."""
    parcel = build_parcel_from_ai_data(data, source_path)
    if parcel is None:
        return AIRecognitionResult(
            error="AI response missing valid boundary data",
            raw_response=data,
            notes=data.get("notes", ""),
        )

    return AIRecognitionResult(
        parcels=[parcel],
        raw_response=data,
        confidence=float(data.get("confidence", 0.5)),
        notes=data.get("notes", ""),
    )


def _shoelace_area(coords: list[tuple[float, float]]) -> float:
    """Compute polygon area via shoelace formula."""
    n = len(coords)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    return abs(area) / 2.0


def _polygon_perimeter(coords: list[tuple[float, float]]) -> float:
    """Compute polygon perimeter."""
    import math

    n = len(coords)
    perimeter = 0.0
    for i in range(n):
        j = (i + 1) % n
        dx = coords[j][0] - coords[i][0]
        dy = coords[j][1] - coords[i][1]
        perimeter += math.sqrt(dx * dx + dy * dy)
    return perimeter
