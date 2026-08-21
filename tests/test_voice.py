from unittest.mock import Mock

from router.intent_router import IntentRouter
from skills.vision import VisionSkill
from voice.conversation import ConversationLoop


def test_conversation_passes_wake_word_command_to_assistant():
    assistant = Mock()
    assistant.chat.return_value = "Your screen shows VS Code."
    loop = ConversationLoop(assistant, listener=Mock(), whisper=Mock())

    result = loop.handle_transcription("Hey Karen, what is on my screen")

    assert result == "Your screen shows VS Code."
    assistant.chat.assert_called_once_with("what is on my screen")


def test_conversation_ignores_transcription_without_wake_word():
    assistant = Mock()
    loop = ConversationLoop(assistant, listener=Mock(), whisper=Mock())

    assert loop.handle_transcription("what is on my screen") is None
    assistant.chat.assert_not_called()


def test_conversation_command_errors_do_not_escape_handler():
    assistant = Mock()
    assistant.chat.side_effect = RuntimeError("vision unavailable")
    loop = ConversationLoop(assistant, listener=Mock(), whisper=Mock())

    assert loop.handle_transcription("Hey Karen, what is on my screen") is None


def test_conversation_routes_screen_command_to_existing_vision_skill():
    capture = Mock()
    capture.capture.return_value = object()
    service = Mock()
    service.describe.return_value = "A code editor is visible."
    vision = VisionSkill(capture=capture, vision_service=service)
    router = IntentRouter()
    assistant = Mock()
    assistant.chat.side_effect = lambda command: vision.execute(router.route(command))
    loop = ConversationLoop(assistant, listener=Mock(), whisper=Mock())

    result = loop.handle_transcription("Hey Karen, what is on my screen")

    assert result == "A code editor is visible."
    assistant.chat.assert_called_once_with("what is on my screen")
    capture.capture.assert_called_once_with()
    service.describe.assert_called_once()
