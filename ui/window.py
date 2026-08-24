"""Compact Karen desktop window."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import theme
from .components import ConversationView, action_button, configure_styles
from .controller import UIController
from .state import ConversationMessage, KarenStatus, UIState


class KarenWindow:
    """Presentation-only window with a small, controller-friendly surface."""

    def __init__(self, root: tk.Tk, controller: UIController | None = None, state: UIState | None = None) -> None:
        self.root = root
        self.controller = controller
        self.state = state or UIState()
        configure_styles(root)
        root.title("Karen")
        root.geometry("390x540")
        root.minsize(320, 420)
        root.configure(background=theme.BG)
        self.status_label = ttk.Label(root, style="Status.TLabel")
        self._build()
        self.set_status(self.state.status)
        for message in self.state.messages:
            self.conversation.add_message(message)

    def _build(self) -> None:
        shell = ttk.Frame(self.root, style="Karen.TFrame", padding=14)
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
        actions = ttk.Frame(shell, style="Karen.TFrame")
        actions.grid(row=3, column=0, sticky="ew")
        for column in range(3):
            actions.columnconfigure(column, weight=1)
        action_button(actions, "💬  History", "history", self._action).grid(row=0, column=0, sticky="ew")
        action_button(actions, "🧩  Skills", "skills", self._action).grid(row=0, column=1, sticky="ew")
        action_button(actions, "⚙  Settings", "settings", self._action).grid(row=0, column=2, sticky="ew")

    def _action(self, action: str) -> None:
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
        self.root.destroy()
