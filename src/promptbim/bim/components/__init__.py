"""Building component library — 74 component definitions with supplier data."""

from promptbim.bim.components.base import (
    ComponentCategory,
    ComponentDef,
    PriceRange,
    SupplierInfo,
)
from promptbim.bim.components.registry import ComponentRegistry

__all__ = [
    "ComponentCategory",
    "ComponentDef",
    "ComponentRegistry",
    "PriceRange",
    "SupplierInfo",
]
