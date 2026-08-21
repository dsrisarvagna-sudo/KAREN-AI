"""Explicit, one-shot screen understanding."""

from __future__ import annotations

from typing import Any, Optional

from router.schemas import Intent
from skills.base import Skill
from vision.screen_capture import ScreenCapture, ScreenCaptureError
from vision.vision_service import VisionInputError, VisionService


class VisionSkill(Skill):
    """Coordinate one screen capture and one vision-model request."""

    def __init__(
        self,
        capture: Optional[Any] = None,
        vision_service: Optional[Any] = None,
    ) -> None:
        self._capture = capture or ScreenCapture()
        self._vision_service = vision_service or VisionService()

    def can_handle(self, command: Any) -> bool:
        if isinstance(command, Intent):
            return command.skill == "vision"
        return False

    def execute(self, command: Any) -> str:
        if not self.can_handle(command):
            return "Vision skill cannot handle this command."

        try:
            image = self._capture.capture()
            return self._vision_service.describe(image)
        except Exception:
            return "I couldn't analyze the screen right now."
