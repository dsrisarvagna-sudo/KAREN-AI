from config.settings import AI_MODE
from ai.ollama_client import chat as ollama_chat


class AIManager:
    def __init__(self):
        self.mode = AI_MODE.lower()

    def chat(self, message, history=None):
        if self.mode == "ollama":
            return ollama_chat(message, history)

        elif self.mode == "openai":
            # We'll implement this later
            return "OpenAI mode is not implemented yet."

        return "Invalid AI mode."