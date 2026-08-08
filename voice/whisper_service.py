from __future__ import annotations

import numpy as np
from faster_whisper import WhisperModel
from config.settings import WHISPER_MODEL


class WhisperService:
    def __init__(self) -> None:
        print("Loading Whisper model...")
        self.model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        print("Whisper loaded successfully.")

    def transcribe(self, audio, sample_rate: int = 16000) -> str:
        if isinstance(audio, np.ndarray):
            audio = audio.astype(np.float32, copy=False) / 32768.0
        segments, _ = self.model.transcribe(audio, language="en", beam_size=5)
        return " ".join(segment.text for segment in segments).strip()
