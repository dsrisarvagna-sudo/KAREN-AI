"""Focused tests for the standalone screenshot capture component."""

import pytest

from vision.screen_capture import ScreenCapture, ScreenCaptureError


def test_screen_capture_imports() -> None:
    assert ScreenCapture is not None


def test_capture_returns_image() -> None:
    try:
        image = ScreenCapture().capture()
    except ScreenCaptureError as exc:
        pytest.skip(f"Screen capture unavailable in this environment: {exc}")

    assert image.width > 0
    assert image.height > 0
    assert image.size == (image.width, image.height)
    assert len(image.rgb) == image.width * image.height * 3
