"""Local, file-backed conversation history repository."""

from __future__ import annotations

import json
from pathlib import Path

from .conversation import Conversation, Message, utc_now


class ConversationHistory:
    """Store one JSON document per conversation under a local data directory."""

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        self.storage_dir = Path(storage_dir or "data/conversations")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def create_conversation(self, title: str = "New Conversation") -> Conversation:
        conversation = Conversation(title=title or "New Conversation")
        self._save(conversation)
        return conversation

    def add_message(self, conversation_id: str, role: str, content: str) -> Message:
        conversation = self.get_conversation(conversation_id)
        if conversation is None:
            raise KeyError(f"conversation not found: {conversation_id}")
        message = Message(role=role, content=content)
        conversation.messages.append(message)
        if role == "user" and conversation.title == "New Conversation":
            conversation.title = self._title_from(content)
        conversation.updated_at = utc_now()
        self._save(conversation)
        return message

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        path = self._path(conversation_id)
        if not path.exists():
            return None
        return Conversation.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list_conversations(self) -> list[Conversation]:
        conversations = [self.get_conversation(path.stem) for path in self.storage_dir.glob("*.json")]
        return sorted((item for item in conversations if item is not None),
                      key=lambda item: item.updated_at, reverse=True)

    def update_conversation(self, conversation: Conversation) -> Conversation:
        conversation.updated_at = utc_now()
        self._save(conversation)
        return conversation

    def delete_conversation(self, conversation_id: str) -> bool:
        path = self._path(conversation_id)
        if not path.exists():
            return False
        path.unlink()
        return True

    def _path(self, conversation_id: str) -> Path:
        if not conversation_id or Path(conversation_id).name != conversation_id:
            raise ValueError("invalid conversation id")
        return self.storage_dir / f"{conversation_id}.json"

    def _save(self, conversation: Conversation) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._path(conversation.conversation_id).write_text(
            json.dumps(conversation.to_dict(), indent=2), encoding="utf-8")

    @staticmethod
    def _title_from(content: str) -> str:
        title = " ".join(content.split())
        return title[:57].rstrip() + "..." if len(title) > 60 else title or "New Conversation"
