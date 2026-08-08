class ConversationMemory:

    def __init__(self):

        self.messages = []

    def set_system_prompt(self, prompt):

        # Remove old system prompt if it exists
        self.messages = [
            msg for msg in self.messages
            if msg["role"] != "system"
        ]

        self.messages.insert(
            0,
            {
                "role": "system",
                "content": prompt
            }
        )

    def add_user(self, message):

        self.messages.append(
            {
                "role": "user",
                "content": message
            }
        )

    def add_assistant(self, message):

        self.messages.append(
            {
                "role": "assistant",
                "content": message
            }
        )

    def get_history(self):

        return self.messages