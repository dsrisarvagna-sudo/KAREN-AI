"""Explicit, one-shot screen metadata inspection."""

from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
from dataclasses import dataclass
from typing import Optional

from .screen_capture import ScreenCapture, ScreenCaptureError


@dataclass(frozen=True)
class ScreenInfo:
    """Structured metadata for the screen at one point in time."""

    screen_width: int
    screen_height: int
    screenshot_width: int
    screenshot_height: int
    active_window: Optional[str] = None
    application: Optional[str] = None


class ScreenAwareness:
    """Inspect the current screen once when explicitly requested."""

    def __init__(self, capture: Optional[ScreenCapture] = None) -> None:
        self._capture = capture or ScreenCapture()

    def inspect(self) -> ScreenInfo:
        """Capture the primary screen and return metadata about it.

        The screenshot remains in memory only for the duration of this call;
        no image or screen metadata is written to disk or Karen's memory.

        Raises:
            ScreenCaptureError: If the screen cannot be captured.
        """
        screenshot = self._capture.capture()
        width, height = screenshot.size
        active_window, application = self._active_window_info()
        return ScreenInfo(
            screen_width=width,
            screen_height=height,
            screenshot_width=width,
            screenshot_height=height,
            active_window=active_window,
            application=application,
        )

    @staticmethod
    def _active_window_info() -> tuple[Optional[str], Optional[str]]:
        """Return focused-window metadata on Windows, when available."""
        if os.name != "nt":
            return None, None

        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None, None

        title_length = user32.GetWindowTextLengthW(hwnd)
        title_buffer = ctypes.create_unicode_buffer(title_length + 1)
        user32.GetWindowTextW(hwnd, title_buffer, len(title_buffer))
        title = title_buffer.value or None

        process_id = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
        application = ScreenAwareness._process_name(process_id.value)
        return title, application

    @staticmethod
    def _process_name(process_id: int) -> Optional[str]:
        """Return a focused process executable name without requiring pywin32."""
        if not process_id:
            return None

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
        if not handle:
            return None
        try:
            size = wintypes.DWORD(260)
            buffer = ctypes.create_unicode_buffer(size.value)
            if not kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
                return None
            return os.path.basename(buffer.value) or None
        finally:
            kernel32.CloseHandle(handle)
