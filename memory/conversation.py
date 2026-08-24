"""Serializable conversation data types used by Karen's history service."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Message:
    role: str
    content: str
    message_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if self.role not in {"user", "assistant"}:
            raise ValueError("message role must be 'user' or 'assistant'")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Message":
        return cls(role=data["role"], content=data["content"],
                   message_id=data["message_id"], timestamp=data["timestamp"])


@dataclass
class Conversation:
    title: str = "New Conversation"
    conversation_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    messages: list[Message] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["messages"] = [message.to_dict() for message in self.messages]
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Conversation":
        return cls(title=data.get("title", "New Conversation"), conversation_id=data["conversation_id"],
                   created_at=data["created_at"], updated_at=data["updated_at"],
                   messages=[Message.from_dict(item) for item in data.get("messages", [])])
