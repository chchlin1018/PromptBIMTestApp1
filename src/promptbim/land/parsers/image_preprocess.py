"""Image preprocessing for land parcel recognition.

Handles image loading, normalization, format conversion (HEIC→JPG, PDF→PNG),
and base64 encoding for the Claude Vision API.
"""

from __future__ import annotations

import base64
import io
from pathlib import Path

from PIL import Image

from promptbim.debug import get_logger

logger = get_logger("land.image_preprocess")

SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".webp", ".heic", ".heif", ".pdf",
}

MAX_DIMENSION = 2048
JPEG_QUALITY = 85


def is_supported_image(file_path: str | Path) -> bool:
    """Check if the file extension is a supported image format."""
    return Path(file_path).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS


def load_image(file_path: str | Path) -> Image.Image:
    """Load an image file, handling HEIC and PDF conversion.

    Returns a PIL Image in RGB mode.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _pdf_to_image(path)
    elif suffix in (".heic", ".heif"):
        return _heic_to_image(path)
    else:
        img = Image.open(path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        return img


def normalize_image(
    img: Image.Image,
    max_dimension: int = MAX_DIMENSION,
    enhance_contrast: bool = True,
) -> Image.Image:
    """Resize and optionally enhance contrast for better AI recognition."""
    # Resize if too large
    w, h = img.size
    if max(w, h) > max_dimension:
        scale = max_dimension / max(w, h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        logger.info("Resized image from %dx%d to %dx%d", w, h, new_w, new_h)

    if enhance_contrast:
        try:
            from PIL import ImageEnhance

            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
        except Exception:
            pass

    return img


def image_to_base64(img: Image.Image, format: str = "JPEG") -> str:
    """Encode a PIL Image to base64 string."""
    buf = io.BytesIO()
    img.save(buf, format=format, quality=JPEG_QUALITY)
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


def prepare_for_vision_api(
    file_path: str | Path,
    max_dimension: int = MAX_DIMENSION,
) -> tuple[str, str]:
    """Load, normalize, and encode an image for the Claude Vision API.

    Returns:
        (base64_data, media_type) tuple ready for API call.
    """
    logger.debug("Preparing image for Vision API: %s", file_path)
    img = load_image(file_path)
    original_size = img.size
    img = normalize_image(img, max_dimension=max_dimension)
    logger.debug("Image: original=%dx%d, processed=%dx%d", original_size[0], original_size[1], img.size[0], img.size[1])

    suffix = Path(file_path).suffix.lower()
    if suffix == ".png":
        b64 = image_to_base64(img, format="PNG")
        media_type = "image/png"
    else:
        b64 = image_to_base64(img, format="JPEG")
        media_type = "image/jpeg"

    logger.debug("Encoded: format=%s, base64_len=%d", media_type, len(b64))
    return b64, media_type


def _pdf_to_image(path: Path) -> Image.Image:
    """Convert first page of a PDF to a PIL Image."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(path))
        page = doc[0]
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        return img
    except ImportError:
        try:
            import pdfplumber

            with pdfplumber.open(str(path)) as pdf:
                page = pdf.pages[0]
                pil_img = page.to_image(resolution=200).original
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")
                return pil_img
        except ImportError:
            raise ImportError(
                "PDF support requires PyMuPDF or pdfplumber. "
                "Install: pip install PyMuPDF  OR  pip install pdfplumber"
            )


def _heic_to_image(path: Path) -> Image.Image:
    """Convert HEIC/HEIF image to PIL Image."""
    try:
        from pillow_heif import register_heif_opener

        register_heif_opener()
        img = Image.open(path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        return img
    except ImportError:
        raise ImportError(
            "HEIC support requires pillow-heif. Install: pip install pillow-heif"
        )
