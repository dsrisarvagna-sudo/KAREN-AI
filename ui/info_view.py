"""Small, non-persistent Settings and Skills dashboard views."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from collections.abc import Callable


class InfoView(ttk.Frame):
    def __init__(self, parent: tk.Misc, title: str, on_back: Callable[[], None]) -> None:
        super().__init__(parent, style="Karen.TFrame", padding=14)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        header = ttk.Frame(self, style="Karen.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(1, weight=1)
        ttk.Button(header, text="‹ Back", style="Action.TButton", command=on_back).grid(row=0, column=0, sticky="w")
        ttk.Label(header, text=title, style="Title.TLabel").grid(row=0, column=1, padx=8)
        self.body = ttk.Frame(self, style="Surface.TFrame", padding=18)
        self.body.grid(row=1, column=0, sticky="nsew")
        self.body.columnconfigure(0, weight=1)

    def section(self, title: str) -> None:
        row = self.body.grid_size()[1]
        ttk.Label(self.body, text=title.upper(), style="Section.TLabel").grid(
            row=row, column=0, sticky="w", pady=(14 if row else 0, 6))

    def item(self, label: str, value: str) -> None:
        row = self.body.grid_size()[1]
        line = ttk.Frame(self.body, style="Surface.TFrame")
        line.grid(row=row, column=0, sticky="ew", pady=3)
        line.columnconfigure(1, weight=1)
        ttk.Label(line, text=label, style="InfoLabel.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(line, text=value, style="InfoValue.TLabel").grid(row=0, column=1, sticky="e")


class SettingsView(InfoView):
    def __init__(self, parent: tk.Misc, on_back: Callable[[], None]) -> None:
        super().__init__(parent, "KAREN — SETTINGS", on_back)
        self.section("Voice")
        self.item("Wake word", "Hey Karen")
        self.item("Microphone", "Default")
        self.item("Speaker", "Default")
        self.section("AI")
        self.item("Model", "Llama 3.2")
        self.section("Vision")
        self.item("Model", "Qwen2.5-VL 3B")
        self.section("Appearance")
        self.item("Theme", "Dark")
        ttk.Label(self.body, text="Settings will become configurable in a later milestone.",
                  style="MutedSurface.TLabel", wraplength=300).grid(
                      row=self.body.grid_size()[1], column=0, sticky="w", pady=(20, 0))


class SkillsView(InfoView):
    def __init__(self, parent: tk.Misc, on_back: Callable[[], None]) -> None:
        super().__init__(parent, "KAREN — SKILLS", on_back)
        for skill in ("Browser", "Calculator", "VS Code", "Files", "Screenshot", "OCR", "Vision"):
            self.section(skill)
            self.item("Status", "● Available")
