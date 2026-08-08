import os

from skills.base import Skill
from router.schemas import Intent


class VSCodeSkill(Skill):

    def can_handle(self, command):

        if isinstance(command, Intent):

            return False

        command = command.lower()

        return (
            "vs code" in command
            or "visual studio code" in command
            or "code editor" in command
        )

    def execute(self, command):

        os.system("code")

        return "Opening Visual Studio Code."
