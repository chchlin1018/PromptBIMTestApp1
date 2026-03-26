"""Schema version compatibility checks."""

from __future__ import annotations

CURRENT_SCHEMA_VERSION = "2.4.0"

# Minimum schema version that is forward-compatible
MIN_COMPATIBLE_VERSION = "2.0.0"


def check_schema_compatibility(data_version: str) -> tuple[bool, str]:
    """Check if a schema version is compatible with the current version.

    Returns:
        (compatible, message) tuple.
    """
    try:
        data_parts = _parse_version(data_version)
        min_parts = _parse_version(MIN_COMPATIBLE_VERSION)
    except ValueError as e:
        return False, f"Invalid version format: {e}"

    if data_parts < min_parts:
        return False, (
            f"Schema version {data_version} is too old. "
            f"Minimum compatible: {MIN_COMPATIBLE_VERSION}. "
            f"Data migration required."
        )

    return True, f"Schema version {data_version} is compatible"


def _parse_version(version_str: str) -> tuple[int, ...]:
    """Parse a semver string into a tuple of ints."""
    parts = version_str.split(".")
    return tuple(int(p) for p in parts)
