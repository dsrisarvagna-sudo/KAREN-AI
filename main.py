from core.assistant import KarenAssistant
from utils.startup import boot
from voice.conversation import ConversationLoop
import sys


def main():

    boot()

    assistant = KarenAssistant()

    conversation = ConversationLoop(assistant)

    print("=" * 40)
    print("Karen AI v0.6")
    print("=" * 40)

    if "--typed" in sys.argv:
        conversation.run_typed()
    else:
        conversation.run()


if __name__ == "__main__":
    main()
