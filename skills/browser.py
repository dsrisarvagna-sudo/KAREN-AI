import webbrowser
from urllib.parse import quote_plus

from skills.base import Skill
from router.schemas import Intent


class BrowserSkill(Skill):

    _TARGET_URLS = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
    }
    _TARGET_LABELS = {
        "youtube": "YouTube",
        "google": "Google",
    }

    def can_handle(self, command):

        if isinstance(command, Intent):

            return command.skill == "browser"

        command = command.lower()

        return (
            "google" in command
            or "browser" in command
            or "chrome" in command
            or "youtube" in command
        )

    def execute(self, command):

        if isinstance(command, Intent):

            if command.action == "search" and command.query:

                query = quote_plus(command.query.strip())
                webbrowser.open(f"https://www.google.com/search?q={query}")

                return f"Searching for {command.query}."

            if command.target in self._TARGET_URLS:
                target = command.target
                webbrowser.open(self._TARGET_URLS[target])
                return f"Opening {self._TARGET_LABELS[target]}."

            webbrowser.open("https://www.google.com")

            return "Opening browser."

        command = command.lower()

        if "youtube" in command:

            webbrowser.open(self._TARGET_URLS["youtube"])

            return "Opening YouTube."

        if "google" in command:

            webbrowser.open(self._TARGET_URLS["google"])

            return "Opening Google."

        webbrowser.open("https://www.google.com")

        return "Opening browser."
