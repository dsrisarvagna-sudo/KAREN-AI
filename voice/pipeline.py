from voice.listener import Listener
from voice.whisper_service import WhisperService


class VoicePipeline:

    def __init__(self, assistant):
        self.listener = Listener()
        self.whisper = WhisperService()
        self.assistant = assistant

    def run_once(self):

        audio_file = self.listener.listen()

        user_message = self.whisper.transcribe(audio_file)

        print(f"\nYou: {user_message}")

        if not user_message.strip():
            print("Nothing detected.")
            return

        reply = self.assistant.chat(user_message)

        print(f"\nKaren: {reply}")