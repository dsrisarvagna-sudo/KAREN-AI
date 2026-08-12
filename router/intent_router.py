import re

from router.schemas import Intent


class IntentRouter:

    _BROWSER_TARGETS = ("youtube", "google", "browser", "chrome")

    def route(self, command: str) -> Intent:

        command = (command or "").lower().strip()

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
