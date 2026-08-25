"""Launch the standalone Karen v7.1 desktop UI foundation."""

from __future__ import annotations

import argparse
import tkinter as tk

from .state import ConversationMessage, UIState
from .window import KarenWindow


def create_app(*, start_runtime: bool = True, runtime: KarenRuntime | None = None) -> tuple[tk.Tk, KarenWindow]:
    root = tk.Tk()
    state = UIState(messages=[
        ConversationMessage("You", "Show me what you can do."),
        ConversationMessage("Karen", "I’m ready. This is the v7.1 UI foundation."),
    ])
    if runtime is None and start_runtime:
        from core.runtime import KarenRuntime
        runtime = KarenRuntime()
    window = KarenWindow(root, state=state, runtime=runtime)
    if start_runtime:
        runtime.start()
    return root, window


def main() -> None:
    parser = argparse.ArgumentParser(description="Karen AI v7.1 desktop UI")
    parser.add_argument("--smoke-test", action="store_true", help="construct and close the UI without entering mainloop")
    args = parser.parse_args()
    root, _window = create_app(start_runtime=not args.smoke_test)
    if args.smoke_test:
        root.update_idletasks()
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()
