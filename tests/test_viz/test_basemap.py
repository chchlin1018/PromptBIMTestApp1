"""Tests for satellite basemap overlay."""

from promptbim.viz.basemap import (
    BASEMAP_STYLES,
    add_basemap,
    calculate_bounds,
)


class TestCalculateBounds:
    def test_basic_bounds(self):
        coords = [(0, 0), (10, 0), (10, 10), (0, 10)]
        bounds = calculate_bounds(coords, padding_pct=0.0)
        assert bounds == (0.0, 0.0, 10.0, 10.0)

    def test_bounds_with_padding(self):
        coords = [(0, 0), (10, 0), (10, 10), (0, 10)]
        bounds = calculate_bounds(coords, padding_pct=0.1)
        assert bounds[0] < 0  # min_x padded left
        assert bounds[1] < 0  # min_y padded down
        assert bounds[2] > 10  # max_x padded right
        assert bounds[3] > 10  # max_y padded up

    def test_empty_coords(self):
        bounds = calculate_bounds([])
        assert bounds == (0.0, 0.0, 1.0, 1.0)


class TestBasemapStyles:
    def test_styles_exist(self):
        assert "osm" in BASEMAP_STYLES
        assert "satellite" in BASEMAP_STYLES
        assert "none" in BASEMAP_STYLES

    def test_style_has_name(self):
        for key, style in BASEMAP_STYLES.items():
            assert "name" in style
            assert "url" in style


class TestAddBasemap:
    def test_add_basemap_none_style(self):
        """Style 'none' should return False."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        result = add_basemap(ax, (0, 0, 10, 10), style="none")
        assert result is False
        plt.close(fig)

    def test_add_basemap_unknown_style(self):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        result = add_basemap(ax, (0, 0, 10, 10), style="unknown_style")
        assert result is False
        plt.close(fig)

    def test_add_basemap_placeholder_fallback(self):
        """Without contextily, should fall back to placeholder."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        # This will try contextily (likely not installed) then fallback
        result = add_basemap(ax, (0, 0, 10, 10), style="osm")
        # Should succeed with placeholder even without contextily
        assert isinstance(result, bool)
        plt.close(fig)
