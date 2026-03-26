"""Shared utilities for land parsers."""

from __future__ import annotations

from pathlib import Path

from promptbim.constants import MAX_LAND_FILE_SIZE_MB
from promptbim.debug import get_logger

logger = get_logger("land.parsers.utils")


def check_file_size(file_path: Path) -> None:
    """Raise ValueError if file exceeds MAX_LAND_FILE_SIZE_MB."""
    size_bytes = file_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > MAX_LAND_FILE_SIZE_MB:
        raise ValueError(
            f"File {file_path.name} is {size_mb:.1f} MB, "
            f"exceeding the {MAX_LAND_FILE_SIZE_MB} MB limit"
        )
    logger.debug("File size check OK: %s (%.2f MB)", file_path.name, size_mb)
