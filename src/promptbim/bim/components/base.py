"""Component definitions — semantic, geometry, and product data layers."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ComponentCategory(str, Enum):
    STRUCTURAL = "structural"
    ENVELOPE = "envelope"
    INTERIOR = "interior"
    OPENING = "opening"
    VERTICAL_TRANSPORT = "vertical_transport"
    MEP = "mep"
    FIXTURE = "fixture"
    SITE = "site"


class PriceRange(BaseModel):
    """Reference price range."""

    currency: str = "TWD"
    min_price: float
    max_price: float
    unit: str  # "per_unit", "per_sqm", "per_m", "per_set"
    source: str = ""
    updated: str = ""


class SupplierInfo(BaseModel):
    """Supplier information."""

    name: str
    brand: str = ""
    model_number: str = ""
    catalog_url: str = ""
    country: str = ""
    price: PriceRange | None = None


class ComponentDef(BaseModel):
    """Complete building component definition."""

    # Identity
    id: str
    category: ComponentCategory
    name_zh: str
    name_en: str
    description_zh: str = ""
    description_en: str = ""

    # IFC mapping
    ifc_class: str
    ifc_predefined_type: str = ""
    omniclass_code: str = ""
    uniformat_code: str = ""

    # Parametric dimensions
    parameters: dict[str, dict] = {}

    # 3D model
    geometry_mode: str = "parametric"  # "parametric" | "mesh" | "mesh+param"
    mesh_file: str | None = None
    mesh_source: str = ""
    mesh_license: str = ""

    # Suppliers & pricing
    suppliers: list[SupplierInfo] = []

    # AI hints
    ai_keywords: list[str] = []
    ai_placement_rules: str = ""
