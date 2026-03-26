"""Tests for the building component library."""

import pytest

from promptbim.bim.components.base import ComponentCategory, PriceRange, SupplierInfo
from promptbim.bim.components.load_all import load_all_components
from promptbim.bim.components.registry import ComponentRegistry


@pytest.fixture(autouse=True)
def _load_components():
    """Ensure components are loaded before each test."""
    ComponentRegistry.clear()
    load_all_components()
    yield
    ComponentRegistry.clear()


class TestComponentRegistry:
    def test_total_count_at_least_74(self):
        assert ComponentRegistry.count() >= 74

    def test_all_categories_have_components(self):
        for cat in ComponentCategory:
            comps = ComponentRegistry.list_by_category(cat)
            assert len(comps) > 0, f"Category {cat.value} has no components"

    def test_get_by_id(self):
        comp = ComponentRegistry.get("elevator_passenger")
        assert comp is not None
        assert comp.name_zh == "客用電梯"
        assert comp.ifc_class == "IfcTransportElement"

    def test_get_nonexistent_returns_none(self):
        assert ComponentRegistry.get("nonexistent_xyz") is None

    def test_search_chinese_keyword(self):
        results = ComponentRegistry.search(["電梯"])
        assert len(results) >= 3
        ids = [r.id for r in results]
        assert "elevator_passenger" in ids

    def test_search_english_keyword(self):
        results = ComponentRegistry.search(["elevator"])
        assert len(results) >= 3

    def test_search_with_category_filter(self):
        results = ComponentRegistry.search(["門"], category=ComponentCategory.OPENING)
        assert len(results) >= 3
        for r in results:
            assert r.category == ComponentCategory.OPENING

    def test_search_no_results(self):
        results = ComponentRegistry.search(["zzzznonexistent"])
        assert len(results) == 0

    def test_list_by_category(self):
        structural = ComponentRegistry.list_by_category(ComponentCategory.STRUCTURAL)
        assert len(structural) == 12

    def test_all_components_returns_full_list(self):
        all_comps = ComponentRegistry.all_components()
        assert len(all_comps) >= 74


class TestComponentDef:
    def test_elevator_has_suppliers(self):
        comp = ComponentRegistry.get("elevator_passenger")
        assert len(comp.suppliers) >= 5
        # Check supplier has price
        suppliers_with_price = [s for s in comp.suppliers if s.price]
        assert len(suppliers_with_price) >= 5

    def test_component_has_required_fields(self):
        for comp in ComponentRegistry.all_components():
            assert comp.id, "Component missing id"
            assert comp.name_zh, f"{comp.id} missing name_zh"
            assert comp.name_en, f"{comp.id} missing name_en"
            assert comp.ifc_class, f"{comp.id} missing ifc_class"
            assert comp.category in ComponentCategory

    def test_component_ids_unique(self):
        all_comps = ComponentRegistry.all_components()
        ids = [c.id for c in all_comps]
        assert len(ids) == len(set(ids)), "Duplicate component IDs found"

    def test_structural_category_count(self):
        comps = ComponentRegistry.list_by_category(ComponentCategory.STRUCTURAL)
        assert len(comps) == 12

    def test_vertical_transport_count(self):
        comps = ComponentRegistry.list_by_category(ComponentCategory.VERTICAL_TRANSPORT)
        assert len(comps) == 12

    def test_opening_count(self):
        comps = ComponentRegistry.list_by_category(ComponentCategory.OPENING)
        assert len(comps) == 10


class TestPriceRange:
    def test_price_range_model(self):
        pr = PriceRange(min_price=1000, max_price=5000, unit="per_unit")
        assert pr.currency == "TWD"
        assert pr.min_price < pr.max_price


class TestSupplierInfo:
    def test_supplier_with_price(self):
        s = SupplierInfo(
            name="Test Supplier",
            brand="TestBrand",
            price=PriceRange(min_price=100, max_price=200, unit="per_unit"),
        )
        assert s.price is not None
        assert s.price.min_price == 100
