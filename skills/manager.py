from skills.browser import BrowserSkill
from skills.vscode import VSCodeSkill
from skills.calculator import CalculatorSkill
from skills.vision import VisionSkill


class SkillManager:

    def __init__(self):

        self.skills = {
            "browser": BrowserSkill(),
            "vscode": VSCodeSkill(),
            "calculator": CalculatorSkill(),
            "vision": VisionSkill()
        }


    def execute(self, intent):

        if intent.skill == "chat":
            return None

        skill = self.skills.get(intent.skill)

        if skill:

            return skill.execute(intent)

        return None
