import webbrowser

from skills.base import Skill
from router.schemas import Intent


class BrowserSkill(Skill):

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

                webbrowser.open(f"https://www.google.com/search?q={command.query}")

                return f"Searching for {command.query}."

            if command.target == "youtube":

                webbrowser.open("https://youtube.com")

                return "Opening YouTube."

            if command.target == "google":

                webbrowser.open("https://google.com")

                return "Opening Google."

            webbrowser.open("https://google.com")

            return "Opening browser."

        command = command.lower()

        if "youtube" in command:

            webbrowser.open("https://youtube.com")

            return "Opening YouTube."

        if "google" in command:

            webbrowser.open("https://google.com")

            return "Opening Google."

        webbrowser.open("https://google.com")

        return "Opening browser."
