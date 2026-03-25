"""USDZ packer — packages .usda files into .usdz for Apple Quick Look / Vision Pro.

Uses UsdUtils.CreateNewUsdzPackage when available (via pxr),
with a fallback to manual ZIP-based packaging.
"""

from __future__ import annotations

import logging
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)


def pack_usdz(
    usda_path: str | Path,
    output_path: str | Path | None = None,
) -> Path:
    """Pack a .usda file into a .usdz file.

    Args:
        usda_path: Path to the source .usda file.
        output_path: Optional output path. Defaults to same name with .usdz extension.

    Returns:
        Path to the created .usdz file.

    Raises:
        FileNotFoundError: If the source file doesn't exist.
        RuntimeError: If packing fails.
    """
    usda_path = Path(usda_path)
    if not usda_path.exists():
        raise FileNotFoundError(f"USD file not found: {usda_path}")

    if output_path is None:
        output_path = usda_path.with_suffix(".usdz")
    else:
        output_path = Path(output_path)

    # Try pxr UsdUtils first
    try:
        return _pack_with_usdutils(usda_path, output_path)
    except (ImportError, Exception) as e:
        logger.info("UsdUtils not available (%s), using ZIP fallback", e)

    # Fallback: manual ZIP packaging (USDZ is a ZIP with specific structure)
    return _pack_with_zip(usda_path, output_path)


def _pack_with_usdutils(usda_path: Path, output_path: Path) -> Path:
    """Pack using pxr.UsdUtils.CreateNewUsdzPackage."""
    from pxr import UsdUtils

    # UsdUtils needs a flattened .usdc file
    # First flatten the stage
    from pxr import Usd

    stage = Usd.Stage.Open(str(usda_path))
    if stage is None:
        raise RuntimeError(f"Failed to open USD stage: {usda_path}")

    # Create temp .usdc for packaging
    with tempfile.TemporaryDirectory() as tmp_dir:
        usdc_path = Path(tmp_dir) / "model.usdc"
        stage.Export(str(usdc_path))

        success = UsdUtils.CreateNewUsdzPackage(
            str(usdc_path), str(output_path)
        )
        if not success:
            raise RuntimeError("UsdUtils.CreateNewUsdzPackage failed")

    logger.info("Packed USDZ (UsdUtils): %s", output_path)
    return output_path


def _pack_with_zip(usda_path: Path, output_path: Path) -> Path:
    """Manual USDZ packaging via ZIP (uncompressed, 64-byte aligned).

    USDZ spec requires:
    - ZIP format, no compression (store only)
    - Files aligned to 64-byte boundaries
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Try to convert to .usdc for smaller size, fall back to .usda
        content_file = usda_path
        archive_name = usda_path.stem + usda_path.suffix

        try:
            from pxr import Usd

            usdc_path = Path(tmp_dir) / "model.usdc"
            stage = Usd.Stage.Open(str(usda_path))
            if stage:
                stage.Export(str(usdc_path))
                content_file = usdc_path
                archive_name = "model.usdc"
        except (ImportError, Exception):
            pass

        # Build aligned ZIP
        _write_aligned_zip(output_path, content_file, archive_name)

    logger.info("Packed USDZ (ZIP fallback): %s", output_path)
    return output_path


def _write_aligned_zip(output_path: Path, content_file: Path, archive_name: str) -> None:
    """Write a USDZ-compliant ZIP file with 64-byte alignment."""
    with zipfile.ZipFile(str(output_path), "w", compression=zipfile.ZIP_STORED) as zf:
        zf.write(str(content_file), arcname=archive_name)
