class Skill:

    def can_handle(self, command: str) -> bool:
        return False

    def execute(self, command: str) -> str:
        return "Skill not implemented."