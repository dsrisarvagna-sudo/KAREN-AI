"""In-memory capture of the primary display."""

from __future__ import annotations

from typing import Any


class ScreenCaptureError(RuntimeError):
    """Raised when the primary screen cannot be captured."""


class ScreenCapture:
    """Capture the current primary screen without creating a persistent file."""

    def capture(self) -> Any:
        """Return the current primary screen as an in-memory ``mss`` image.

        The returned object exposes ``width``, ``height``, ``size``, ``rgb``,
        and ``pixels`` attributes and can be converted by a future vision
        service without requiring an intermediate screenshot file.

        Raises:
            ScreenCaptureError: If no display is available or capture fails.
        """
        try:
            import mss

            with mss.MSS() as screen:
                monitor = screen.monitors[1]
                return screen.grab(monitor)
        except Exception as exc:
            raise ScreenCaptureError("Unable to capture the primary screen") from exc
