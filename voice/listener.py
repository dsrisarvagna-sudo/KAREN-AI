from __future__ import annotations

import numpy as np
import sounddevice as sd


class VoiceListener:
    """Record short microphone windows and return PCM audio in memory."""

    def __init__(self, sample_rate: int = 16000, duration: float = 4.0) -> None:
        self.sample_rate = sample_rate
        self.duration = duration

    def listen(self) -> np.ndarray:
        print("\nListening...")
        try:
            audio = sd.rec(int(self.duration * self.sample_rate), samplerate=self.sample_rate,
                           channels=1, dtype="int16")
            sd.wait()
        except Exception as exc:
            raise RuntimeError(f"Microphone recording failed: {exc}") from exc
        return np.asarray(audio[:, 0], dtype=np.int16).copy()


# Compatibility for existing imports.
Listener = VoiceListener
