import ollama
from config.settings import OLLAMA_MODEL


def chat(message, history):
    messages = history if history else [
        {"role": "user", "content": message}
    ]
    #print("\n========== SYSTEM PROMPT ==========\n")
    #print(messages[0]["content"])
    #print("\n===================================\n")
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=messages
    )

    return response["message"]["content"]
