"""Small boundary between the desktop UI and future Karen integrations."""

from __future__ import annotations

from typing import Protocol


class UIController(Protocol):
    """Optional callbacks a future adapter may implement.

    The v7.1 window only renders data and emits button intents.  It does not
    know about models, recording, wake words, automation, or agent planning.
    """

    def on_ui_action(self, action: str) -> None:
        """Handle a presentation-layer action such as ``history``."""

