from router.intent_router import IntentRouter
from router.ai_router import AIRouter
from router.schemas import Intent


class HybridRouter:

    def __init__(self):

        self.keyword_router = IntentRouter()
        self.ai_router = AIRouter()

    def route(self, command):

        intent = self.keyword_router.route(command)

        # If keyword router found a real skill,
        # execute it immediately.

        if intent.skill != "chat":

            return intent

        # Otherwise ask AI

        ai_intent = self.ai_router.route(command)

        return Intent(**ai_intent)