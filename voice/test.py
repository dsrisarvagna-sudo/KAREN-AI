"""Manual microphone smoke test: python -m voice.test"""

from voice.listener import VoiceListener
from voice.whisper_service import WhisperService


def main():
    text = WhisperService().transcribe(VoiceListener().listen())
    print(f"\nYou said: {text or '[nothing detected]'}")


if __name__ == "__main__":
    main()
