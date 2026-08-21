import numpy as np
import pytest

from voice.wake_word import WakeWordDetector, detect_wake_word


def test_text_wake_word_extracts_inline_command():
    result = detect_wake_word("Hey Karen open YouTube")
    assert result.detected is True
    assert result.command == "open YouTube"


def test_text_wake_word_extracts_screen_command():
    result = detect_wake_word("Hey Karen, what is on my screen")

    assert result.detected is True
    assert result.command == "what is on my screen"


def test_text_without_wake_word_is_ignored():
    result = detect_wake_word("what is recursion")
    assert result.detected is False
    assert result.command == ""


class FakeModel:
    def __init__(self, scores):
        self.scores = scores
        self.calls = 0

    def predict(self, audio):
        self.calls += 1
        assert audio.dtype == np.int16
        return self.scores


def test_detector_returns_highest_configured_match():
    model = FakeModel({"hey_karen": 0.7, "karen": 0.9})
    detector = WakeWordDetector(("Hey Karen", "Karen"), 0.5, model=model)

    match = detector.detect(np.zeros(1280, dtype=np.int16))

    assert match is not None
    assert match.phrase == "karen"
    assert match.score == pytest.approx(0.9)
    assert model.calls == 1


def test_detector_applies_sensitivity():
    detector = WakeWordDetector(("Karen",), 0.8, model=FakeModel({"karen": 0.79}))

    assert detector.detect(b"\0\0" * 1280) is None


def test_detector_rejects_empty_phrases():
    with pytest.raises(ValueError):
        WakeWordDetector(())
