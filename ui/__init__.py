"""Karen's presentation-only desktop UI.

The package deliberately does not import Karen's core, voice, or vision
subsystems.  Integrations can provide a controller implementing the small
interface in :mod:`ui.controller` later.
"""

from .controller import UIController
from .state import ConversationMessage, KarenStatus, UIState
from .window import KarenWindow

__all__ = [
    "ConversationMessage",
    "KarenStatus",
    "KarenWindow",
    "UIController",
    "UIState",
]
