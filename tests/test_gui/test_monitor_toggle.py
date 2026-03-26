"""Tests for gui/monitor_toggle.py — monitoring point visibility toggle."""


class TestMonitorToggleImport:
    def test_import(self):
        from promptbim.gui.monitor_toggle import MonitorTogglePanel

        assert MonitorTogglePanel is not None

    def test_category_labels_exist(self):
        from promptbim.gui.monitor_toggle import CATEGORY_LABELS

        assert len(CATEGORY_LABELS) == 8

    def test_category_colors_exist(self):
        from promptbim.gui.monitor_toggle import CATEGORY_COLORS

        assert len(CATEGORY_COLORS) == 8
        for color in CATEGORY_COLORS.values():
            assert len(color) == 3
