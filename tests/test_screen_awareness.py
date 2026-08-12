"""Focused tests for v6.2 screen awareness."""

from types import SimpleNamespace

import pytest

from vision.screen_awareness import ScreenAwareness, ScreenInfo
from vision.screen_capture import ScreenCaptureError


def test_screen_awareness_imports() -> None:
    assert ScreenAwareness is not None


def test_inspect_uses_screen_capture() -> None:
    capture = SimpleNamespace(capture=lambda: SimpleNamespace(size=(320, 200)))
    info = ScreenAwareness(capture).inspect()

    assert isinstance(info, ScreenInfo)
    assert info.screen_width == 320
    assert info.screen_height == 200
    assert info.screenshot_width == 320
    assert info.screenshot_height == 200


def test_inspect_obtains_screen_information() -> None:
    try:
        info = ScreenAwareness().inspect()
    except ScreenCaptureError as exc:
        pytest.skip(f"Screen awareness unavailable in this environment: {exc}")

    assert isinstance(info, ScreenInfo)
    assert info.screen_width > 0
    assert info.screen_height > 0
    assert info.screenshot_width > 0
    assert info.screenshot_height > 0


def test_inspect_handles_headless_display() -> None:
    class UnavailableCapture:
        def capture(self):
            raise ScreenCaptureError("display unavailable")

    with pytest.raises(ScreenCaptureError):
        ScreenAwareness(UnavailableCapture()).inspect()
