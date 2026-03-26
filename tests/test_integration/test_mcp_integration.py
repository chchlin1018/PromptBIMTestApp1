"""P24 Task 22: MCP Server integration tests.

Tests the MCP server tool functions directly (without starting the server).
"""

from __future__ import annotations

import pytest


class TestMCPServerIntegration:
    """Test MCP server tools end-to-end."""

    def test_import_land_tool(self):
        """Test that import_land creates a valid land parcel."""
        from promptbim.mcp.server import import_land

        result = import_land(
            boundary=[[0, 0], [30, 0], [30, 25], [0, 25]],
            name="MCP Test Parcel",
            area_sqm=750.0,
        )
        assert "MCP Test Parcel" in result
        assert "750" in result or "area" in result.lower()

    def test_get_session_info_tool(self):
        """Test that get_session_info returns session state."""
        from promptbim.mcp.server import get_session_info

        result = get_session_info()
        assert isinstance(result, str)
        assert "land" in result.lower() or "session" in result.lower() or "state" in result.lower()

    def test_clear_cache_tool(self):
        """Test that clear_cache resets server state."""
        from promptbim.mcp.server import clear_cache

        result = clear_cache()
        assert "clear" in result.lower() or "reset" in result.lower()
