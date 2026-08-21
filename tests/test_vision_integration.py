"""Tests for v6.5 screen-understanding routing and orchestration."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from router.intent_router import IntentRouter
from router.schemas import Intent
from skills.vision import VisionSkill


@pytest.mark.parametrize(
    "command",
    [
        "what is on my screen",
        "what's on my screen",
        "describe my screen",
        "what do you see on my screen",
        "look at my screen",
        "analyze my screen",
    ],
)
def test_screen_commands_route_to_vision(command: str) -> None:
    intent = IntentRouter().route(command)

    assert intent == Intent(skill="vision", action="screen_understanding")


def test_vision_skill_captures_and_describes_image() -> None:
    screenshot = object()
    capture = Mock()
    capture.capture.return_value = screenshot
    service = Mock()
    service.describe.return_value = "A code editor is visible."

    result = VisionSkill(capture=capture, vision_service=service).execute(
        Intent(skill="vision", action="screen_understanding")
    )

    assert result == "A code editor is visible."
    capture.capture.assert_called_once_with()
    service.describe.assert_called_once_with(screenshot)


def test_vision_skill_handles_capture_errors() -> None:
    capture = Mock()
    capture.capture.side_effect = RuntimeError("display unavailable")
    service = Mock()

    result = VisionSkill(capture=capture, vision_service=service).execute(
        Intent(skill="vision", action="screen_understanding")
    )

    assert result == "I couldn't analyze the screen right now."
    service.describe.assert_not_called()


def test_vision_skill_handles_vision_errors() -> None:
    capture = SimpleNamespace(capture=lambda: object())
    service = Mock()
    service.describe.side_effect = RuntimeError("model unavailable")

    result = VisionSkill(capture=capture, vision_service=service).execute(
        Intent(skill="vision", action="screen_understanding")
    )

    assert result == "I couldn't analyze the screen right now."


def test_existing_browser_and_ai_routes_are_preserved() -> None:
    router = IntentRouter()

    browser_intent = router.route("open youtube")
    assert browser_intent.skill == "browser"
    assert browser_intent.action == "open"
    assert browser_intent.target == "youtube"

    ai_intent = router.route("what is recursion?")
    assert ai_intent.skill == "chat"
