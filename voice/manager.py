from voice.listener import Listener
from voice.whisper_service import WhisperService


class VoiceManager:

    def __init__(self):

        self.listener = Listener()
        self.whisper = WhisperService()

    def get_command(self):

        print("🎤 Listening...")

        audio = self.listener.listen()

        print("📝 Transcribing...")

        text = self.whisper.transcribe(audio)

        return text.strip()