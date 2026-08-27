import subprocess

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
        if isinstance(command, Intent):
            if command.action in ("open_file", "open_folder") and command.target:
                # shell=False — argument list, never a constructed shell string
                subprocess.Popen(["code", command.target], shell=False)
                return f"Opening {command.target} in VS Code."
        # Default: just open VS Code with no arguments
        subprocess.Popen(["code"], shell=False)
        return "Opening Visual Studio Code."
