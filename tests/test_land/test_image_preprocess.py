"""Tests for image preprocessing module."""

import io
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from promptbim.land.parsers.image_preprocess import (
    SUPPORTED_IMAGE_EXTENSIONS,
    image_to_base64,
    is_supported_image,
    load_image,
    normalize_image,
    prepare_for_vision_api,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "land_images"


def _create_test_image(tmp_path: Path, name: str = "test.jpg", size=(100, 80)) -> Path:
    """Create a small test image."""
    img = Image.new("RGB", size, color=(128, 200, 100))
    path = tmp_path / name
    img.save(path)
    return path


class TestIsSupported:
    def test_jpg_supported(self):
        assert is_supported_image("photo.jpg")

    def test_jpeg_supported(self):
        assert is_supported_image("photo.JPEG")

    def test_png_supported(self):
        assert is_supported_image("map.png")

    def test_tiff_supported(self):
        assert is_supported_image("scan.tiff")

    def test_bmp_supported(self):
        assert is_supported_image("old.bmp")

    def test_webp_supported(self):
        assert is_supported_image("modern.webp")

    def test_heic_supported(self):
        assert is_supported_image("iphone.heic")

    def test_pdf_supported(self):
        assert is_supported_image("cadastral.pdf")

    def test_unsupported_format(self):
        assert not is_supported_image("data.csv")

    def test_dxf_not_image(self):
        assert not is_supported_image("drawing.dxf")


class TestLoadImage:
    def test_load_jpg(self, tmp_path):
        path = _create_test_image(tmp_path, "test.jpg")
        img = load_image(path)
        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"

    def test_load_png(self, tmp_path):
        path = _create_test_image(tmp_path, "test.png")
        img = load_image(path)
        assert isinstance(img, Image.Image)

    def test_load_rgba_converts_to_rgb(self, tmp_path):
        img = Image.new("RGBA", (50, 50), color=(128, 200, 100, 255))
        path = tmp_path / "test_rgba.png"
        img.save(path)
        loaded = load_image(path)
        assert loaded.mode == "RGB"

    def test_load_real_fixture(self):
        """Load real test image if available."""
        img_path = FIXTURES_DIR / "IMG_1451.JPG"
        if img_path.exists():
            img = load_image(img_path)
            assert isinstance(img, Image.Image)
            assert img.mode == "RGB"
            assert img.size[0] > 0 and img.size[1] > 0


class TestNormalizeImage:
    def test_resize_large_image(self):
        img = Image.new("RGB", (4000, 3000))
        result = normalize_image(img, max_dimension=2048)
        assert max(result.size) <= 2048

    def test_small_image_unchanged(self):
        img = Image.new("RGB", (200, 150))
        result = normalize_image(img, max_dimension=2048)
        assert result.size == (200, 150)

    def test_contrast_enhancement(self):
        img = Image.new("RGB", (100, 100), color=(128, 128, 128))
        result = normalize_image(img, enhance_contrast=True)
        assert isinstance(result, Image.Image)


class TestImageToBase64:
    def test_encode_jpg(self):
        img = Image.new("RGB", (50, 50), color=(255, 0, 0))
        b64 = image_to_base64(img, format="JPEG")
        assert isinstance(b64, str)
        assert len(b64) > 0
        # Verify it's valid base64
        import base64
        decoded = base64.standard_b64decode(b64)
        assert len(decoded) > 0

    def test_encode_png(self):
        img = Image.new("RGB", (50, 50))
        b64 = image_to_base64(img, format="PNG")
        assert isinstance(b64, str)
        assert len(b64) > 0


class TestPrepareForVisionAPI:
    def test_prepare_jpg(self, tmp_path):
        path = _create_test_image(tmp_path, "test.jpg")
        b64, media_type = prepare_for_vision_api(path)
        assert isinstance(b64, str)
        assert media_type == "image/jpeg"
        assert len(b64) > 100

    def test_prepare_png(self, tmp_path):
        path = _create_test_image(tmp_path, "test.png")
        b64, media_type = prepare_for_vision_api(path)
        assert media_type == "image/png"

    def test_prepare_real_fixture(self):
        img_path = FIXTURES_DIR / "IMG_1452.JPG"
        if img_path.exists():
            b64, media_type = prepare_for_vision_api(img_path)
            assert media_type == "image/jpeg"
            assert len(b64) > 1000
