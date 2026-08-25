"""Compact Karen desktop window."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from . import theme
from .components import ConversationView, action_button, configure_styles
from .controller import UIController
from .history_view import HistoryView
from .info_view import SettingsView, SkillsView
from .state import ConversationMessage, KarenStatus, UIState
from memory.history import ConversationHistory
from core.events import RuntimeEvent, RuntimeEventType


class KarenWindow:
    """Presentation-only window with a small, controller-friendly surface."""

    def __init__(self, root: tk.Tk, controller: UIController | None = None, state: UIState | None = None,
                 history: ConversationHistory | None = None, runtime: Any | None = None) -> None:
        self.root = root
        self.controller = controller
        self.state = state or UIState()
        self.history = history or ConversationHistory()
        self.runtime = runtime
        self._poll_id: str | None = None
        self.current_conversation_id: str | None = None
        configure_styles(root)
        root.title("Karen")
        root.geometry("430x650")
        root.minsize(360, 500)
        root.configure(background=theme.BG)
        self.status_label = ttk.Label(root, style="Status.TLabel")
        self._build()
        self.set_status(self.state.status)
        for message in self.state.messages:
            self.conversation.add_message(message)
        if self.runtime is not None:
            self.root.protocol("WM_DELETE_WINDOW", self.close)
            self._poll_runtime()

    def _build(self) -> None:
        shell = ttk.Frame(self.root, style="Karen.TFrame", padding=14)
        self.shell = shell
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(1, weight=1)
        header = ttk.Frame(shell, style="Karen.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(1, weight=1)
        ttk.Label(header, text="KAREN", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        self.status_label.grid(in_=header, row=0, column=1, sticky="e")
        content = ttk.Frame(shell, style="Surface.TFrame", padding=(18, 18, 10, 10))
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(2, weight=1)
        ttk.Label(content, text="Good evening, SPIDY", style="Greeting.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(content, text="Karen is ready.", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 12))
        self.conversation = ConversationView(content)
        self.conversation.grid(row=2, column=0, sticky="nsew")
        mic = ttk.Frame(shell, style="Surface.TFrame", padding=(14, 10))
        mic.grid(row=2, column=0, sticky="ew", pady=(10, 10))
        ttk.Label(mic, text="🎤  Listening...", style="Mic.TLabel").pack(anchor="w")
        input_frame = ttk.Frame(shell, style="Karen.TFrame")
        input_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var)
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.input_entry.insert(0, "Ask Karen...")
        self.input_entry.bind("<FocusIn>", self._clear_input_placeholder)
        self.input_entry.bind("<Return>", self._submit_text)
        ttk.Button(input_frame, text="Send", style="Action.TButton", command=self._submit_text).grid(row=0, column=1)
        self.runtime_status_label = ttk.Label(mic, text="🎤 Waiting for wake word", style="Mic.TLabel")
        self.runtime_status_label.pack(anchor="w")
        mic.winfo_children()[0].pack_forget()
        actions = ttk.Frame(shell, style="Karen.TFrame")
        actions.grid(row=4, column=0, sticky="ew")
        for column in range(3):
            actions.columnconfigure(column, weight=1)
        action_button(actions, "💬  History", "history", self._action).grid(row=0, column=0, sticky="ew")
        action_button(actions, "🧩  Skills", "skills", self._action).grid(row=0, column=1, sticky="ew")
        action_button(actions, "⚙  Settings", "settings", self._action).grid(row=0, column=2, sticky="ew")

        self.history_view = HistoryView(self.root, self.history, self.show_main, self._set_current_conversation)
        self.settings_view = SettingsView(self.root, self.show_main)
        self.skills_view = SkillsView(self.root, self.show_main)

    def _set_current_conversation(self, conversation: object) -> None:
        conversation_id = getattr(conversation, "conversation_id", None)
        if conversation_id is not None:
            self.current_conversation_id = conversation_id
            if self.runtime is not None:
                self.runtime.current_conversation_id = conversation_id

    def _clear_input_placeholder(self, _event: object = None) -> None:
        if self.input_var.get() == "Ask Karen...":
            self.input_var.set("")

    def _submit_text(self, _event: object = None) -> str:
        command = self.input_var.get().strip()
        if command == "Ask Karen...":
            command = ""
        if command and self.runtime is not None:
            self.runtime.submit_text(command)
            self.input_var.set("")
        return "break"

    def _poll_runtime(self) -> None:
        if self.runtime is None:
            return
        for event in self.runtime.poll_events():
            self._handle_runtime_event(event)
        self._poll_id = self.root.after(50, self._poll_runtime)

    def _handle_runtime_event(self, event: RuntimeEvent) -> None:
        status = {
            RuntimeEventType.SYSTEM_STARTING: "🟡 Starting...",
            RuntimeEventType.SYSTEM_READY: "🟢 Online",
            RuntimeEventType.WAKE_WORD_WAITING: "🟢 Waiting for wake word",
            RuntimeEventType.RECORDING_STARTED: "🎤 Listening...",
            RuntimeEventType.TRANSCRIPTION_READY: "🧠 Thinking...",
            RuntimeEventType.THINKING_STARTED: "🧠 Thinking...",
            RuntimeEventType.VISION_STARTED: "👀 Looking...",
            RuntimeEventType.SPEAKING_STARTED: "🔊 Speaking...",
            RuntimeEventType.SPEAKING_FINISHED: "🟢 Waiting for wake word",
            RuntimeEventType.SHUTDOWN: "Stopping...",
            RuntimeEventType.ERROR: f"🔴 {event.text or 'Karen unavailable'}",
        }.get(event.type)
        if status is not None:
            self.state.set_runtime_status(status)
            self.status_label.configure(
                text=status,
                foreground=theme.OFFLINE if event.type is RuntimeEventType.ERROR else theme.ACCENT,
            )
            self.runtime_status_label.configure(text=status)
        if event.type is RuntimeEventType.RESPONSE_READY and event.role:
            self.add_message("You" if event.role == "user" else "Karen", event.text)

    def show_history(self) -> None:
        self._hide_secondary_views()
        self.shell.pack_forget()
        self.history_view.refresh()
        self.history_view.pack(fill="both", expand=True)

    def show_main(self) -> None:
        self._hide_secondary_views()
        self.shell.pack(fill="both", expand=True)

    def show_settings(self) -> None:
        self._hide_secondary_views()
        self.shell.pack_forget()
        self.settings_view.pack(fill="both", expand=True)

    def show_skills(self) -> None:
        self._hide_secondary_views()
        self.shell.pack_forget()
        self.skills_view.pack(fill="both", expand=True)

    def _hide_secondary_views(self) -> None:
        self.history_view.pack_forget()
        self.settings_view.pack_forget()
        self.skills_view.pack_forget()

    def _action(self, action: str) -> None:
        if action == "history":
            self.show_history()
        elif action == "skills":
            self.show_skills()
        elif action == "settings":
            self.show_settings()
        if self.controller is not None:
            self.controller.on_ui_action(action)

    def set_status(self, status: KarenStatus | str) -> None:
        self.state.set_status(status)
        self.status_label.configure(text=self.state.status.display,
                                    foreground=theme.OFFLINE if self.state.status is KarenStatus.OFFLINE else theme.ACCENT)

    def add_message(self, speaker: str, text: str) -> None:
        self.state.add_message(speaker, text)
        self.conversation.add_message(ConversationMessage(speaker, text))

    def close(self) -> None:
        if self._poll_id is not None:
            self.root.after_cancel(self._poll_id)
            self._poll_id = None
        if self.runtime is not None:
            self.runtime.stop()
        self.root.destroy()
