from ai.manager import AIManager
from ai.memory import ConversationMemory

from router.hybrid_router import HybridRouter

from skills.manager import SkillManager

from memory.manager import MemoryManager
from memory.prompt_builder import PromptBuilder

from voice.speaker import Speaker


class KarenAssistant:

    def __init__(self):

        self.ai = AIManager()

        self.memory = ConversationMemory()

        self.memory_manager = MemoryManager()

        self.speaker = Speaker()

        self.router = HybridRouter()

        self.skill_manager = SkillManager()

    def chat(self, user_message):

        # Save conversation
        self.memory.add_user(user_message)

        # Learn from user
        self.memory_manager.process(user_message)

        memory = self.memory_manager.get_memory()

        system_prompt = PromptBuilder.build(memory)

        self.memory.set_system_prompt(system_prompt)

        # Try Skills First
        intent = self.router.route(user_message)

        reply = self.skill_manager.execute(intent)

        # No skill? Ask AI
        if reply is None:

            reply = self.ai.chat(
                user_message,
                self.memory.get_history()
            )

        # Save reply
        self.memory.add_assistant(reply)

        # Speak reply
        self.speaker.speak(reply)

        return reply

        
