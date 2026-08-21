from __future__ import annotations

from typing import Any, Callable

from voice.listener import VoiceListener
from voice.whisper_service import WhisperService
from voice.wake_word import WakeWordResult, detect_wake_word


class ConversationLoop:
    """Keep microphone input separate from KarenAssistant."""

    def __init__(
        self,
        assistant: Any,
        *,
        listener: Any | None = None,
        whisper: Any | None = None,
        wake_word_detector: Callable[[str], WakeWordResult] = detect_wake_word,
    ):
        self.assistant = assistant
        self.listener = listener or VoiceListener()
        self.whisper = whisper
        self._wake_word_detector = wake_word_detector

    def handle_transcription(self, text: str) -> str | None:
        """Handle one already-transcribed voice utterance."""
        wake = self._wake_word_detector(text)
        if not wake.detected:
            return None
        if not wake.command:
            self.assistant.speaker.speak("Yes?")
            return "Yes?"
        return self._dispatch(wake.command)

    def _dispatch(self, command: str) -> str | None:
        try:
            return self.assistant.chat(command)
        except Exception as exc:
            print(f"Voice command error: {exc}. Returning to wake-word listening.")
            return None

    def run(self):
        self.whisper = self.whisper or WhisperService()
        print("\nKaren is Online.\nWaiting for wake word...")
        while True:
            try:
                text = self.whisper.transcribe(self.listener.listen())
                if text.lower().strip(" .!?") in {"bye", "exit", "shutdown karen"}:
                    print("Karen shutting down...")
                    break
                wake = self._wake_word_detector(text)
                if not wake.detected:
                    continue
                print(f"\nHeard: {text}")
                command = wake.command
                if not command:
                    self.assistant.speaker.speak("Yes?")
                    print("Karen: Yes?\nListening for your command...")
                    command = self.whisper.transcribe(self.listener.listen()).strip()
                if not command:
                    continue
                if command.lower().strip(" .!?") in {"bye", "exit", "shutdown karen"}:
                    print("Karen shutting down...")
                    break
                print(f"You: {command}\n")
                response = self._dispatch(command)
                print(f"Karen: {response}\nWaiting for wake word...")
            except KeyboardInterrupt:
                print("\nKaren shutting down...")
                break
            except Exception as exc:
                print(f"Voice error: {exc}. Returning to wake-word listening.")

    def run_typed(self):
        """Retain a typed-input mode for development and fallback use."""
        while True:
            try:
                command = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nKaren shutting down...")
                return
            if command.lower() in {"bye", "exit", "shutdown karen"}:
                return
            if command:
                print(f"Karen: {self.assistant.chat(command)}")
