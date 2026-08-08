# AI Configuration

AI_MODE = "ollama"
OLLAMA_MODEL = "llama3.2"
WHISPER_MODEL = "base"

APP_NAME = "Karen AI"
VERSION = "0.5.0"

VOICE_TIMEOUT = 5
SAMPLE_RATE = 16000

# Wake-word configuration.  OpenWakeWord identifies models, rather than raw
# phrases, so WAKE_WORD_MODEL_PATH may be either a directory containing the
# configured models or a mapping of phrase -> model file.
WAKE_PHRASES = ("hey karen", "okay karen", "karen")
WAKE_WORD = WAKE_PHRASES[0]  # Backwards-compatible alias.
WAKE_WORD_SENSITIVITY = 0.5
WAKE_WORD_TIMEOUT = 10.0
WAKE_WORD_MODEL_PATH = None

# Audio capture/VAD settings used by VoiceEngine.
VOICE_SILENCE_TIMEOUT = 0.8
VOICE_MIN_SPEECH_DURATION = 0.25
VOICE_MAX_RECORDING_DURATION = 30.0

# Kept for callers using the old name.
ACTIVATION_TIMEOUT = WAKE_WORD_TIMEOUT
LOG_LEVEL = "INFO"
