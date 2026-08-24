"""Scrollable conversation list and message detail view."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from collections.abc import Callable
from datetime import datetime

from memory.conversation import Conversation
from memory.history import ConversationHistory

from . import theme


class HistoryView(ttk.Frame):
    def __init__(self, parent: tk.Misc, history: ConversationHistory, on_back: Callable[[], None],
                 on_select: Callable[[Conversation | None], None] | None = None) -> None:
        super().__init__(parent, style="Karen.TFrame", padding=14)
        self.history, self.on_back, self.on_select = history, on_back, on_select
        self._conversations: list[Conversation] = []
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        header = ttk.Frame(self, style="Karen.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(1, weight=1)
        ttk.Button(header, text="‹ Back", style="Action.TButton", command=on_back).grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="KAREN — HISTORY", style="Title.TLabel").grid(row=0, column=1, padx=8)
        ttk.Button(header, text="＋ New", style="Action.TButton", command=self._new_conversation).grid(row=0, column=2, sticky="e")
        body = ttk.Frame(self, style="Surface.TFrame", padding=10)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.columnconfigure(2, weight=3)
        body.rowconfigure(0, weight=1)
        self.listbox = tk.Listbox(body, background=theme.SURFACE, foreground=theme.TEXT,
                                  selectbackground=theme.ACCENT_DARK, relief="flat", borderwidth=0,
                                  font=(theme.FONT, 10), activestyle="none")
        list_scroll = ttk.Scrollbar(body, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=list_scroll.set)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        list_scroll.grid(row=0, column=1, sticky="ns")
        self.detail = tk.Text(body, wrap="word", state="disabled", relief="flat", borderwidth=0,
                              background=theme.SURFACE, foreground=theme.TEXT, font=(theme.FONT, 10), padx=12)
        self.detail.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        self.listbox.bind("<<ListboxSelect>>", self._selected)
        self.refresh()

    def refresh(self) -> None:
        self._conversations = self.history.list_conversations()
        self.listbox.delete(0, "end")
        for conversation in self._conversations:
            self.listbox.insert("end", f"{conversation.title}\n{self._display_time(conversation.updated_at)}")
        self._show(None)

    def _selected(self, _event: object = None) -> None:
        selection = self.listbox.curselection()
        self._show(self._conversations[selection[0]] if selection else None)

    def _show(self, conversation: Conversation | None) -> None:
        if self.on_select is not None:
            self.on_select(conversation)
        self.detail.configure(state="normal")
        self.detail.delete("1.0", "end")
        if conversation is None:
            self.detail.insert("end", "Select a conversation to view its messages.")
        else:
            self.detail.insert("end", f"{conversation.title}\n\n")
            for message in conversation.messages:
                self.detail.insert("end", f"{'You' if message.role == 'user' else 'Karen'}\n", "speaker")
                self.detail.insert("end", f"{message.content}\n\n")
        self.detail.tag_configure("speaker", foreground=theme.ACCENT, font=(theme.FONT, 10, "bold"))
        self.detail.configure(state="disabled")

    def _new_conversation(self) -> None:
        conversation = self.history.create_conversation()
        self.refresh()
        index = next(i for i, item in enumerate(self._conversations)
                     if item.conversation_id == conversation.conversation_id)
        self.listbox.selection_set(index)
        self.listbox.event_generate("<<ListboxSelect>>")

    @staticmethod
    def _display_time(value: str) -> str:
        try:
            return datetime.fromisoformat(value).astimezone().strftime("%b %d, %I:%M %p")
        except ValueError:
            return value
