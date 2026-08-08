from router.schemas import Intent


class IntentRouter:

    def route(self, command: str) -> Intent:

        command = command.lower()

        # Browser
        if any(word in command for word in [
            "google",
            "youtube",
            "browser",
            "chrome"
        ]):

            return Intent(
                skill="browser",
                action="open"
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