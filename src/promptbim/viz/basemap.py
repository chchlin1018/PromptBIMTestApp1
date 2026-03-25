"""Satellite basemap overlay for land parcel map views.

Fetches OpenStreetMap tile images and composites them as a background
beneath the land parcel polygon on the matplotlib canvas.
Uses contextily when available, with a lightweight fallback.
"""

from __future__ import annotations

from promptbim.debug import get_logger as _get_logger
import math
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from matplotlib.axes import Axes

logger = _get_logger("viz.basemap")

# Tile provider URLs (free, no API key required)
OSM_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
ESRI_SATELLITE_URL = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    "World_Imagery/MapServer/tile/{z}/{y}/{x}"
)

# Available basemap styles
BASEMAP_STYLES = {
    "osm": {
        "name": "OpenStreetMap",
        "url": OSM_TILE_URL,
        "attribution": "(C) OpenStreetMap contributors",
    },
    "satellite": {
        "name": "Satellite (Esri)",
        "url": ESRI_SATELLITE_URL,
        "attribution": "(C) Esri, Maxar, Earthstar Geographics",
    },
    "none": {
        "name": "No Basemap",
        "url": None,
        "attribution": "",
    },
}


def add_basemap(
    ax: "Axes",
    bounds: tuple[float, float, float, float],
    crs: str = "EPSG:4326",
    style: str = "osm",
    zoom: int | None = None,
) -> bool:
    """Add a basemap tile layer to a matplotlib axes.

    Args:
        ax: The matplotlib Axes to add the basemap to.
        bounds: (min_x, min_y, max_x, max_y) in the given CRS.
        crs: Coordinate reference system of the bounds.
        style: Basemap style key from BASEMAP_STYLES.
        zoom: Tile zoom level (auto-calculated if None).

    Returns:
        True if basemap was successfully added, False otherwise.
    """
    if style == "none" or style not in BASEMAP_STYLES:
        return False

    provider = BASEMAP_STYLES[style]
    if provider["url"] is None:
        return False

    # Try contextily first
    try:
        return _add_basemap_contextily(ax, bounds, crs, provider)
    except (ImportError, Exception) as e:
        logger.debug("contextily not available: %s", e)

    # Fallback: render a simple background gradient to indicate satellite area
    try:
        return _add_basemap_placeholder(ax, bounds, provider)
    except Exception as e:
        logger.warning("Basemap fallback failed: %s", e)
        return False


def _add_basemap_contextily(
    ax: "Axes",
    bounds: tuple[float, float, float, float],
    crs: str,
    provider: dict,
) -> bool:
    """Add basemap using contextily library."""
    import contextily as cx

    source = provider["url"]
    attribution = provider["attribution"]

    # contextily expects Web Mercator (EPSG:3857) internally
    cx.add_basemap(
        ax,
        crs=crs,
        source=source,
        attribution=attribution,
        zoom="auto",
    )
    return True


def _add_basemap_placeholder(
    ax: "Axes",
    bounds: tuple[float, float, float, float],
    provider: dict,
) -> bool:
    """Add a placeholder background to indicate basemap area.

    Used when contextily is not available. Renders a light terrain-like
    gradient with attribution text.
    """
    min_x, min_y, max_x, max_y = bounds

    # Create a simple gradient background
    gradient = np.linspace(0.85, 0.95, 64).reshape(8, 8)
    ax.imshow(
        gradient,
        extent=[min_x, max_x, min_y, max_y],
        cmap="Greens",
        alpha=0.15,
        aspect="auto",
        zorder=0,
    )

    # Add attribution
    attribution = provider.get("attribution", "")
    if attribution:
        ax.text(
            max_x,
            min_y,
            f" {attribution} ",
            fontsize=6,
            ha="right",
            va="bottom",
            alpha=0.5,
            transform=ax.transData,
        )

    return True


def calculate_bounds(
    coords: list[tuple[float, float]],
    padding_pct: float = 0.1,
) -> tuple[float, float, float, float]:
    """Calculate bounding box from coordinates with padding.

    Returns:
        (min_x, min_y, max_x, max_y)
    """
    if not coords:
        return (0.0, 0.0, 1.0, 1.0)

    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    dx = (max_x - min_x) * padding_pct
    dy = (max_y - min_y) * padding_pct

    return (min_x - dx, min_y - dy, max_x + dx, max_y + dy)
