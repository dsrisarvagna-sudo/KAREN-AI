from datetime import datetime

import pytest

from memory.history import ConversationHistory


def test_create_and_persist_conversation(tmp_path):
    history = ConversationHistory(tmp_path)
    conversation = history.create_conversation()
    assert conversation.title == "New Conversation"
    assert conversation.conversation_id
    assert datetime.fromisoformat(conversation.created_at)
    assert conversation.conversation_id != history.create_conversation().conversation_id

    history.add_message(conversation.conversation_id, "user", "What's on my screen?")
    history.add_message(conversation.conversation_id, "assistant", "I can see a code editor.")
    reopened = ConversationHistory(tmp_path).get_conversation(conversation.conversation_id)
    assert reopened is not None
    assert reopened.title == "What's on my screen?"
    assert [(item.role, item.content) for item in reopened.messages] == [
        ("user", "What's on my screen?"), ("assistant", "I can see a code editor.")
    ]
    assert all(item.message_id and datetime.fromisoformat(item.timestamp) for item in reopened.messages)


def test_list_is_ordered_by_updated_time_and_missing_is_safe(tmp_path):
    history = ConversationHistory(tmp_path)
    older = history.create_conversation("Older")
    newer = history.create_conversation("Newer")
    history.add_message(newer.conversation_id, "user", "Latest")
    assert [item.title for item in history.list_conversations()] == ["Newer", "Older"]
    assert history.get_conversation("missing") is None
    assert history.delete_conversation(older.conversation_id)
    assert not history.delete_conversation(older.conversation_id)


def test_title_is_simple_first_user_message_and_invalid_role_fails(tmp_path):
    history = ConversationHistory(tmp_path)
    conversation = history.create_conversation()
    long_text = "word " * 20
    history.add_message(conversation.conversation_id, "user", long_text)
    assert history.get_conversation(conversation.conversation_id).title.endswith("...")
    with pytest.raises(ValueError):
        history.add_message(conversation.conversation_id, "system", "not supported")


def test_history_view_imports_without_starting_gui():
    from ui.history_view import HistoryView

    assert HistoryView.__name__ == "HistoryView"
