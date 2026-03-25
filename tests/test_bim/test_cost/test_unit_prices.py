"""Tests for bim/cost/unit_prices_tw.py."""

from promptbim.bim.cost.unit_prices_tw import (
    CATEGORY_LABELS,
    UNIT_PRICES_TWD,
    get_category,
    get_price,
)


class TestUnitPrices:
    def test_all_entries_have_required_keys(self):
        for key, entry in UNIT_PRICES_TWD.items():
            assert "price" in entry, f"{key} missing price"
            assert "unit" in entry, f"{key} missing unit"
            assert "desc" in entry, f"{key} missing desc"
            assert "category" in entry, f"{key} missing category"
            assert entry["price"] > 0, f"{key} price must be positive"

    def test_get_price_known(self):
        assert get_price("slab_sqm") == 2800
        assert get_price("elevator_unit") == 2500000

    def test_get_price_unknown(self):
        assert get_price("nonexistent_key") == 0

    def test_get_category(self):
        assert get_category("hvac_sqm") == "mep"
        assert get_category("brick_wall_sqm") == "envelope"
        assert get_category("nonexistent") == "other"

    def test_category_labels_coverage(self):
        categories_used = {e["category"] for e in UNIT_PRICES_TWD.values()}
        for cat in categories_used:
            assert cat in CATEGORY_LABELS, f"Missing label for category: {cat}"

    def test_minimum_price_entries(self):
        assert len(UNIT_PRICES_TWD) >= 20
