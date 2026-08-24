"""Launch the standalone Karen v7.1 desktop UI foundation."""

from __future__ import annotations

import argparse
import tkinter as tk

from .state import ConversationMessage, UIState
from .window import KarenWindow


def create_app() -> tuple[tk.Tk, KarenWindow]:
    root = tk.Tk()
    state = UIState(messages=[
        ConversationMessage("You", "Show me what you can do."),
        ConversationMessage("Karen", "I’m ready. This is the v7.1 UI foundation."),
    ])
    return root, KarenWindow(root, state=state)


def main() -> None:
    parser = argparse.ArgumentParser(description="Karen AI v7.1 desktop UI")
    parser.add_argument("--smoke-test", action="store_true", help="construct and close the UI without entering mainloop")
    args = parser.parse_args()
    root, _window = create_app()
    if args.smoke_test:
        root.update_idletasks()
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()
