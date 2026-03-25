"""Tests for bim/materials.py."""

from promptbim.bim.materials import (
    MATERIALS,
    get_material,
    roof_material,
    slab_material,
    wall_material,
)


def test_builtin_materials_exist():
    assert len(MATERIALS) >= 5
    assert "concrete" in MATERIALS
    assert "glass" in MATERIALS


def test_get_material_known():
    mat = get_material("glass")
    assert mat.name == "Glass"
    assert mat.transparency > 0


def test_get_material_unknown_falls_back():
    mat = get_material("unknown_xyz")
    assert mat.name == "Concrete"


def test_wall_material_types():
    ext = wall_material("exterior")
    assert ext.name == "Concrete"
    int_ = wall_material("interior")
    assert int_.name == "White Plaster"


def test_slab_material():
    mat = slab_material()
    assert "slab" in mat.name.lower() or "concrete" in mat.name.lower()


def test_roof_material_flat():
    mat = roof_material("flat")
    assert mat is not None


def test_roof_material_gable():
    mat = roof_material("gable")
    assert mat.name == "Roof Tile"
