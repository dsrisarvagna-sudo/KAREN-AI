"""Non-blocking wake-word and speech-to-text voice engine."""

from __future__ import annotations

import queue
import threading
import time
from collections.abc import Callable
from typing import Any

import numpy as np

from config.settings import (
    SAMPLE_RATE,
    VOICE_MIN_SPEECH_DURATION,
    VOICE_SILENCE_TIMEOUT,
    WAKE_PHRASES,
    WAKE_WORD_MODEL_PATH,
    WAKE_WORD_SENSITIVITY,
    WAKE_WORD_TIMEOUT,
)
from voice.wake_word import WakeWordDetector


class VoiceEngine:
    """Continuously listen in a worker thread and emit transcribed commands.

    The sounddevice callback does no model work: it only places small PCM
    chunks into a bounded queue.  OpenWakeWord and Whisper therefore never
    block the application's main thread or the audio callback.
    """

    def __init__(self, assistant: Any | None = None, *, whisper: Any | None = None,
                 detector: WakeWordDetector | None = None, sample_rate: int = SAMPLE_RATE,
                 silence_timeout: float = VOICE_SILENCE_TIMEOUT,
                 max_recording_duration: float = WAKE_WORD_TIMEOUT) -> None:
        self.assistant = assistant
        self.whisper = whisper
        self.sample_rate = sample_rate
        self.silence_timeout = silence_timeout
        self.max_recording_duration = max_recording_duration
        self.detector = detector or WakeWordDetector(
            WAKE_PHRASES, WAKE_WORD_SENSITIVITY, WAKE_WORD_MODEL_PATH
        )
        self._chunks: queue.Queue[np.ndarray] = queue.Queue(maxsize=32)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._stream: Any | None = None
        self._callback: Callable[[str], None] | None = None

    def start(self, on_transcription: Callable[[str], None] | None = None) -> None:
        """Start capture and return immediately."""
        if self._thread and self._thread.is_alive():
            return
        try:
            import sounddevice as sd
        except ImportError as exc:
            raise RuntimeError("sounddevice is required for VoiceEngine") from exc
        self._callback = on_transcription
        self._stop.clear()
        self._stream = sd.InputStream(
            samplerate=self.sample_rate, channels=1, dtype="int16",
            blocksize=1280, callback=self._audio_callback,
        )
        self._stream.start()
        self._thread = threading.Thread(target=self._run, name="karen-voice", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop capture and join the worker briefly."""
        self._stop.set()
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info: Any, status: Any) -> None:
        del frames, time_info, status
        values = indata[:, 0] if getattr(indata, "ndim", 1) > 1 else indata
        chunk = np.asarray(values, dtype=np.int16).copy()
        try:
            self._chunks.put_nowait(chunk)
        except queue.Full:
            try:
                self._chunks.get_nowait()
                self._chunks.put_nowait(chunk)
            except queue.Empty:
                pass

    def _run(self) -> None:
        recording: list[np.ndarray] = []
        recording_started = 0.0
        last_voice = 0.0
        while not self._stop.is_set():
            try:
                chunk = self._chunks.get(timeout=0.2)
            except queue.Empty:
                continue
            if not recording:
                match = self.detector.detect(chunk)
                if match:
                    recording = []
                    recording_started = time.monotonic()
                    last_voice = recording_started
                continue

            recording.append(chunk)
            now = time.monotonic()
            if self._is_voice(chunk):
                last_voice = now
            if (now - last_voice >= self.silence_timeout or
                    now - recording_started >= self.max_recording_duration):
                audio = np.concatenate(recording)
                if len(audio) >= self.sample_rate * VOICE_MIN_SPEECH_DURATION:
                    self._transcribe(audio)
                recording = []
                self.detector.reset()

    @staticmethod
    def _is_voice(chunk: np.ndarray) -> bool:
        return bool(np.sqrt(np.mean(np.square(chunk.astype(np.float32)))) > 450.0)

    def _transcribe(self, audio: np.ndarray) -> None:
        if self.whisper is None:
            from voice.whisper_service import WhisperService
            self.whisper = WhisperService()
        # WhisperService currently accepts a path, while other integrations
        # often accept PCM directly.  Prefer a direct transcribe method and
        # retain a temporary WAV fallback for the existing service.
        try:
            text = self.whisper.transcribe(audio, sample_rate=self.sample_rate)
        except TypeError:
            import tempfile
            from scipy.io.wavfile import write
            wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            try:
                write(wav.name, self.sample_rate, audio)
                wav.close()
                text = self.whisper.transcribe(wav.name)
            finally:
                try:
                    import os
                    os.unlink(wav.name)
                except OSError:
                    pass
        text = (text or "").strip()
        if text and self._callback:
            self._callback(text)
        if text and self.assistant is not None:
            self.assistant.chat(text)

    def __enter__(self) -> "VoiceEngine":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.stop()
