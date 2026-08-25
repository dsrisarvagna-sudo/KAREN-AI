"""Reusable Tkinter widgets used by the Karen window."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from collections.abc import Callable

from .state import ConversationMessage
from . import theme


def configure_styles(root: tk.Misc) -> ttk.Style:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Karen.TFrame", background=theme.BG)
    style.configure("Surface.TFrame", background=theme.SURFACE)
    style.configure("Karen.TLabel", background=theme.BG, foreground=theme.TEXT, font=(theme.FONT, 10))
    style.configure("Muted.TLabel", background=theme.BG, foreground=theme.MUTED, font=(theme.FONT, 9))
    style.configure("Title.TLabel", background=theme.BG, foreground=theme.TEXT, font=(theme.FONT, 12, "bold"))
    style.configure("Greeting.TLabel", background=theme.SURFACE, foreground=theme.TEXT, font=(theme.FONT, 15, "bold"))
    style.configure("Subtitle.TLabel", background=theme.SURFACE, foreground=theme.MUTED, font=(theme.FONT, 10))
    style.configure("Section.TLabel", background=theme.SURFACE, foreground=theme.ACCENT, font=(theme.FONT, 9, "bold"))
    style.configure("InfoLabel.TLabel", background=theme.SURFACE, foreground=theme.TEXT, font=(theme.FONT, 10))
    style.configure("InfoValue.TLabel", background=theme.SURFACE, foreground=theme.MUTED, font=(theme.FONT, 10))
    style.configure("MutedSurface.TLabel", background=theme.SURFACE, foreground=theme.MUTED, font=(theme.FONT, 9))
    style.configure("Status.TLabel", background=theme.BG, foreground=theme.ACCENT, font=(theme.FONT, 9, "bold"))
    style.configure("Mic.TLabel", background=theme.SURFACE_ALT, foreground=theme.ACCENT, font=(theme.FONT, 10, "bold"))
    style.configure("Action.TButton", background=theme.SURFACE, foreground=theme.MUTED, borderwidth=0, padding=(8, 7), font=(theme.FONT, 9))
    style.map("Action.TButton", background=[("active", theme.SURFACE_ALT)], foreground=[("active", theme.TEXT)])
    return style


class ConversationView(ttk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, style="Surface.TFrame", padding=(16, 8, 8, 8))
        self.text = tk.Text(self, height=10, wrap="word", state="disabled", relief="flat", borderwidth=0,
                            background=theme.SURFACE, foreground=theme.TEXT, insertbackground=theme.TEXT,
                            selectbackground=theme.ACCENT_DARK, font=(theme.FONT, 10), padx=2, pady=4)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        self.text.tag_configure("user_label", foreground="#8dc8f4", font=(theme.FONT, 9, "bold"), spacing1=12)
        self.text.tag_configure("user_text", foreground="#e7f2fb", background=theme.USER, lmargin1=8, lmargin2=8, spacing3=8)
        self.text.tag_configure("karen_label", foreground=theme.ACCENT, font=(theme.FONT, 9, "bold"), spacing1=12)
        self.text.tag_configure("karen_text", foreground="#e4f3e9", background=theme.KAREN, lmargin1=8, lmargin2=8, spacing3=8)
        self.text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def add_message(self, message: ConversationMessage) -> None:
        is_user = message.speaker.lower() == "you"
        label_tag = "user_label" if is_user else "karen_label"
        text_tag = "user_text" if is_user else "karen_text"
        self.text.configure(state="normal")
        self.text.insert("end", f"{message.speaker.upper()}\n", label_tag)
        self.text.insert("end", f"{message.text}\n\n", text_tag)
        self.text.configure(state="disabled")
        self.text.see("end")


def action_button(parent: tk.Misc, label: str, action: str, callback: Callable[[str], None]) -> ttk.Button:
    return ttk.Button(parent, text=label, style="Action.TButton", command=lambda: callback(action))
