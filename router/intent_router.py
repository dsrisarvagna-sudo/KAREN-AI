import re

from router.schemas import Intent


class IntentRouter:

    _BROWSER_TARGETS = ("youtube", "google", "browser", "chrome")
    _VISION_PATTERNS = (
        r"\bwhat\s+is\s+on\s+(?:my|the)\s+screen\b",
        r"\bwhat(?:'s|\s+is)\s+on\s+(?:my|the)\s+screen\b",
        r"\bdescribe\s+(?:my|the)\s+screen\b",
        r"\bwhat\s+do\s+you\s+see\s+on\s+(?:my|the)\s+screen\b",
        r"\blook\s+at\s+(?:my|the)\s+screen\b",
        r"\banalyze\s+(?:my|the)\s+screen\b",
    )

    def route(self, command: str) -> Intent:

        command = (command or "").lower().strip()

        if any(re.search(pattern, command) for pattern in self._VISION_PATTERNS):
            return Intent(
                skill="vision",
                action="screen_understanding",
            )

        search_match = re.match(
            r"^search\s+(?:(?:google)\s+)?(?:for\s+)?(.+?)\s*$",
            command,
        )
        if search_match:
            return Intent(
                skill="browser",
                action="search",
                query=search_match.group(1).strip(),
            )

        # Browser
        target = next(
            (word for word in self._BROWSER_TARGETS if re.search(rf"\b{word}\b", command)),
            None,
        )
        if target:

            return Intent(
                skill="browser",
                action="open",
                target=target if target in ("youtube", "google") else None,
            )

        # Calculator
        if "calculator" in command:

            return Intent(
                skill="calculator",
                action="open"
            )

        # VS Code
        if "vs code" in command or "vscode" in command:

            return Intent(
                skill="vscode",
                action="open"
            )

        return Intent(
            skill="chat"
        )
