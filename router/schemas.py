from dataclasses import dataclass
from typing import Optional


@dataclass
class Intent:

    skill: str

    action: Optional[str] = None

    target: Optional[str] = None

    query: Optional[str] = None