"""Manual, opt-in smoke test for the real Qwen2.5-VL model.

Run with ``python -m vision.vision_smoke_test [path-to-image]``. Without a
path, the primary screen is captured in memory and is not written to disk.
"""

from __future__ import annotations

import sys

from .screen_capture import ScreenCapture
from .vision_service import VisionService


def main() -> None:
    image = ScreenCapture().capture() if len(sys.argv) == 1 else sys.argv[1]
    print(VisionService().describe(image))


if __name__ == "__main__":
    main()
