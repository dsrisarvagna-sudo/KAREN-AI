"""Pure UI state types, kept independent of Tkinter and Karen core modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class KarenStatus(str, Enum):
    ONLINE = "Online"
    LISTENING = "Listening"
    THINKING = "Thinking"
    LOOKING = "Looking"
    SPEAKING = "Speaking"
    PAUSED = "Paused"
    OFFLINE = "Offline"

    @property
    def display(self) -> str:
        return {
            self.ONLINE: "🟢 Online",
            self.LISTENING: "🎤 Listening",
            self.THINKING: "🧠 Thinking",
            self.LOOKING: "👀 Looking",
            self.SPEAKING: "🔊 Speaking",
            self.PAUSED: "💤 Paused",
            self.OFFLINE: "🔴 Offline",
        }[self]


@dataclass(frozen=True)
class ConversationMessage:
    speaker: str
    text: str


@dataclass
class UIState:
    status: KarenStatus = KarenStatus.ONLINE
    runtime_status: str = "Online"
    messages: list[ConversationMessage] = field(default_factory=list)

    def set_status(self, status: KarenStatus | str) -> None:
        self.status = status if isinstance(status, KarenStatus) else KarenStatus(status)

    def set_runtime_status(self, status: str) -> None:
        self.runtime_status = status

    def add_message(self, speaker: str, text: str) -> None:
        self.messages.append(ConversationMessage(speaker=speaker, text=text))
