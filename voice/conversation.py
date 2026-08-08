from voice.listener import VoiceListener
from voice.whisper_service import WhisperService
from voice.wake_word import detect_wake_word


class ConversationLoop:
    """Keep microphone input separate from KarenAssistant."""

    def __init__(self, assistant):
        self.assistant = assistant
        self.listener = VoiceListener()
        self.whisper = None

    def run(self):
        self.whisper = WhisperService()
        print("\nKaren is Online.\nWaiting for wake word...")
        while True:
            try:
                text = self.whisper.transcribe(self.listener.listen())
                if text.lower().strip(" .!?") in {"bye", "exit", "shutdown karen"}:
                    print("Karen shutting down...")
                    break
                wake = detect_wake_word(text)
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
                response = self.assistant.chat(command)
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
