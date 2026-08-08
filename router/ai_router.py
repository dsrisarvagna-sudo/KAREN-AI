import json

from ai.ollama_client import chat


class AIRouter:

    def route(self, command):

        prompt = f"""
You are an intent classifier.

Return ONLY valid JSON.

Available skills:

browser
calculator
vscode
chat

Examples

User:
open youtube

Output:
{{"skill":"browser","action":"open","target":"youtube"}}

User:
search google for python

Output:
{{"skill":"browser","action":"search","query":"python"}}

User:
open calculator

Output:
{{"skill":"calculator","action":"open"}}

User:
what is recursion

Output:
{{"skill":"chat"}}

User:
{command}
"""

        response = chat(prompt, [])

        response = chat(prompt, [])

        try:
            return json.loads(response)
        except Exception:
            return {
                "skill": "chat"
    }