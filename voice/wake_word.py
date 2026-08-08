"""OpenWakeWord integration.

The detector is intentionally independent of audio-device code.  It accepts
16 kHz, mono, signed 16-bit PCM chunks and can therefore be used with a
sounddevice callback, a file, or a unit-test fixture.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

import numpy as np


@dataclass(frozen=True)
class WakeWordResult:
    detected: bool
    command: str = ""


def detect_wake_word(text: str, wake_word: str = "karen") -> WakeWordResult:
    """Deterministically detect and remove a spoken Karen wake phrase."""
    normalized = re.sub(r"\s+", " ", (text or "").strip())
    if not normalized:
        return WakeWordResult(False)
    pattern = re.compile(r"\b(?:hey|okay|ok)?\s*" + re.escape(wake_word) + r"\b", re.I)
    match = pattern.search(normalized)
    if match is None:
        return WakeWordResult(False)
    command = (normalized[:match.start()] + " " + normalized[match.end():]).strip(" ,.!?\t")
    return WakeWordResult(True, re.sub(r"\s+", " ", command).strip())


@dataclass(frozen=True)
class WakeWordMatch:
    """A wake-word match returned by :class:`WakeWordDetector`."""

    phrase: str
    score: float


class WakeWordDetector:
    """Small, testable adapter around ``openwakeword.model.Model``.

    ``model`` and ``model_factory`` are injectable so tests do not need to
    download neural-network assets.  In production the model is created only
    when the detector is started, keeping module imports inexpensive.
    """

    def __init__(
        self,
        phrases: Iterable[str],
        sensitivity: float = 0.5,
        model_path: str | Path | Mapping[str, str | Path] | None = None,
        *,
        model: Any | None = None,
        model_factory: Callable[..., Any] | None = None,
    ) -> None:
        self.phrases = tuple(dict.fromkeys(p.strip().lower() for p in phrases if p.strip()))
        if not self.phrases:
            raise ValueError("At least one wake phrase is required")
        if not 0.0 <= sensitivity <= 1.0:
            raise ValueError("Wake-word sensitivity must be between 0 and 1")
        self.sensitivity = sensitivity
        self.model_path = model_path
        self._model = model
        self._model_factory = model_factory
        self._model_keys: dict[str, str] = self._build_model_keys(self._model_files()) if model is not None else {}

    @property
    def model(self) -> Any:
        if self._model is None:
            factory = self._model_factory
            if factory is None:
                try:
                    from openwakeword.model import Model
                except ImportError as exc:
                    raise RuntimeError(
                        "OpenWakeWord is required for wake-word detection; "
                        "install the openwakeword package first"
                    ) from exc
                factory = Model

            models = self._model_files()
            kwargs: dict[str, Any] = {}
            if models:
                kwargs["wakeword_models"] = models
            self._model = factory(**kwargs)
            self._model_keys = self._build_model_keys(models)
        return self._model

    def _model_files(self) -> list[str]:
        path = self.model_path
        if isinstance(path, Mapping):
            return [str(path[p]) for p in self.phrases if p in path]
        if path is None:
            return []
        root = Path(path)
        if root.is_dir():
            return [str(root / f"{phrase.replace(' ', '_')}.onnx") for phrase in self.phrases]
        return [str(root)]

    def _build_model_keys(self, models: list[str]) -> dict[str, str]:
        keys = {}
        for phrase, model in zip(self.phrases, models):
            keys[Path(model).stem.lower()] = phrase
            keys[Path(model).name.lower()] = phrase
        return keys

    def detect(self, audio: np.ndarray | bytes) -> WakeWordMatch | None:
        """Return the highest scoring configured phrase in one audio chunk."""
        samples = np.frombuffer(audio, dtype=np.int16) if isinstance(audio, bytes) else np.asarray(audio)
        scores = self.model.predict(samples.astype(np.int16, copy=False))
        best: WakeWordMatch | None = None
        for key, value in scores.items():
            score = float(value)
            if score < self.sensitivity:
                continue
            phrase = self._model_keys.get(str(key).lower(), str(key).replace("_", " ").lower())
            if phrase not in self.phrases:
                continue
            if best is None or score > best.score:
                best = WakeWordMatch(phrase, score)
        return best

    def reset(self) -> None:
        """Reset OpenWakeWord's rolling prediction state when supported."""
        reset = getattr(self.model, "reset", None)
        if reset is not None:
            reset()
