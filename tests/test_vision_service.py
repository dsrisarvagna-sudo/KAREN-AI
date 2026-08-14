"""Unit tests for the isolated v6.4 vision service."""

from unittest.mock import Mock

import pytest
from PIL import Image

from vision.vision_service import VisionInputError, VisionService


def test_vision_service_imports() -> None:
    assert VisionService is not None


def test_preprocessing_preserves_aspect_ratio() -> None:
    result = VisionService(max_dimension=100).preprocess(Image.new("RGB", (200, 100)))
    assert result.size == (100, 50)


def test_large_screenshot_is_resized() -> None:
    result = VisionService().preprocess(Image.new("RGB", (2560, 1600)))
    assert result.size == (1024, 640)


def test_original_image_is_not_modified() -> None:
    original = Image.new("RGB", (2560, 1600), "red")
    VisionService(max_dimension=100).preprocess(original)
    assert original.size == (2560, 1600)
    assert original.getpixel((0, 0)) == (255, 0, 0)


def test_ollama_receives_model_and_actual_image_input() -> None:
    client = Mock()
    client.chat.return_value = {"message": {"content": "A browser is visible."}}
    service = VisionService(client=client)

    result = service.describe(Image.new("RGB", (20, 10)), prompt="What is here?")

    assert result == "A browser is visible."
    call = client.chat.call_args
    assert call.kwargs["model"] == "qwen2.5vl:3b"
    message = call.kwargs["messages"][0]
    assert message["content"] == "What is here?"
    assert isinstance(message["images"][0], bytes)
    assert message["images"][0].startswith(b"\x89PNG")


def test_default_prompt_is_used() -> None:
    client = Mock()
    client.chat.return_value = {"message": {"content": "Description"}}
    VisionService(client=client).describe(Image.new("RGB", (10, 10)))
    assert client.chat.call_args.kwargs["messages"][0]["content"] == VisionService.DEFAULT_PROMPT


def test_api_failure_is_handled_cleanly() -> None:
    client = Mock()
    client.chat.side_effect = OSError("server unavailable")
    with pytest.raises(RuntimeError, match="Vision model request failed"):
        VisionService(client=client).describe(Image.new("RGB", (10, 10)))


def test_invalid_image_is_rejected() -> None:
    with pytest.raises(VisionInputError):
        VisionService().describe(None)
