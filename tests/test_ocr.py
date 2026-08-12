"""Focused tests for v6.3 OCR."""

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from vision.ocr import OCRInputError, OCRService


def _test_image() -> Image.Image:
    image = Image.new("RGB", (700, 180), "white")
    font = ImageFont.load_default(size=48)
    ImageDraw.Draw(image).text(
        (24, 60), "Karen OCR TEST 123", font=font, fill="black", stroke_width=1
    )
    return image


def test_ocr_imports() -> None:
    assert OCRService is not None


def test_ocr_extracts_known_text() -> None:
    text = OCRService().extract(_test_image())
    assert "Karen" in text
    assert "OCR" in text
    assert "123" in text


def test_ocr_handles_image_without_text() -> None:
    image = Image.new("RGB", (300, 100), "white")
    assert OCRService().extract(image).strip() == ""


def test_ocr_accepts_numpy_image() -> None:
    image = np.full((40, 80, 3), 255, dtype=np.uint8)
    assert OCRService().extract(image) == ""


@pytest.mark.parametrize("invalid", [None, b"", np.empty((0, 0, 3), dtype=np.uint8)])
def test_ocr_rejects_missing_or_invalid_input(invalid) -> None:
    with pytest.raises(OCRInputError):
        OCRService().extract(invalid)
