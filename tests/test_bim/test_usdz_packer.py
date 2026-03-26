"""Tests for USDZ packer."""

import zipfile

import pytest

from promptbim.bim.usdz_packer import pack_usdz


@pytest.fixture
def sample_usda(tmp_path):
    """Create a minimal .usda file for testing."""
    usda = tmp_path / "test_model.usda"
    usda.write_text(
        '#usda 1.0\n(\n    defaultPrim = "World"\n    metersPerUnit = 1\n'
        '    upAxis = "Z"\n)\n\ndef Xform "World"\n{\n}\n'
    )
    return usda


class TestPackUsdz:
    def test_pack_creates_file(self, sample_usda, tmp_path):
        output = tmp_path / "output.usdz"
        result = pack_usdz(sample_usda, output)
        assert result.exists()
        assert result.suffix == ".usdz"

    def test_pack_default_output_path(self, sample_usda):
        result = pack_usdz(sample_usda)
        assert result.exists()
        assert result.suffix == ".usdz"
        assert result.stem == sample_usda.stem
        result.unlink()  # cleanup

    def test_usdz_is_valid_zip(self, sample_usda, tmp_path):
        output = tmp_path / "model.usdz"
        pack_usdz(sample_usda, output)
        assert zipfile.is_zipfile(output)

    def test_usdz_contains_file(self, sample_usda, tmp_path):
        output = tmp_path / "model.usdz"
        pack_usdz(sample_usda, output)
        with zipfile.ZipFile(output) as zf:
            names = zf.namelist()
            assert len(names) >= 1

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            pack_usdz("/nonexistent/file.usda")

    def test_pack_real_usd(self, tmp_path):
        """Test with a real USD stage if pxr is available."""
        try:
            from pxr import Usd, UsdGeom

            usda_path = tmp_path / "real_model.usda"
            stage = Usd.Stage.CreateNew(str(usda_path))
            UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
            xform = UsdGeom.Xform.Define(stage, "/World")
            cube = UsdGeom.Cube.Define(stage, "/World/Cube")
            stage.Save()

            output = tmp_path / "real_model.usdz"
            result = pack_usdz(usda_path, output)
            assert result.exists()
            assert result.stat().st_size > 0
        except ImportError:
            pytest.skip("pxr not available")
