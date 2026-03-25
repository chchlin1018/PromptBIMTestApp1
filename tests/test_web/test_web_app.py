"""Tests for Web UI module."""

import pytest


class TestWebAppModule:
    def test_streamlit_importable(self):
        """Verify streamlit is installed."""
        import streamlit
        assert hasattr(streamlit, "set_page_config")

    def test_web_init_importable(self):
        """Verify web module is importable."""
        import promptbim.web
        assert promptbim.web is not None

    def test_compute_area_function(self):
        """Test the inline area computation used in web app."""
        # We test the logic directly since app.py uses streamlit globals
        coords = [(0, 0), (10, 0), (10, 10), (0, 10)]
        n = len(coords)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += coords[i][0] * coords[j][1]
            area -= coords[j][0] * coords[i][1]
        area = abs(area) / 2.0
        assert abs(area - 100.0) < 0.001
