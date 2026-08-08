from voice.listener import Listener
from voice.whisper_service import WhisperService

listener = Listener()
whisper = WhisperService()

audio_file = listener.listen()

text = whisper.transcribe(audio_file)

print("\nYou said:")
print(text)