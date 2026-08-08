import os

from skills.base import Skill
from router.schemas import Intent


class CalculatorSkill(Skill):

    def can_handle(self, command):

        if isinstance(command, Intent):

            return False

        return "calculator" in command.lower()

    def execute(self, command):

        os.system("calc")

        return "Opening Calculator."
