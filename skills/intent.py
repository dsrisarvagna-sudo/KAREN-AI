import json


class IntentManager:

    def __init__(self, ai):

        self.ai = ai

    def detect(self, user_message, history):

        prompt = f"""
You are an intent classifier.

Your job is NOT to answer the user.

Return ONLY valid JSON.

Available skills:

browser
calculator
vscode
vision

Examples:

User:
Open YouTube

Output:
{{"skill":"browser","action":"open","target":"youtube"}}

User:
Search Nissan Patrol

Output:
{{"skill":"browser","action":"search","query":"nissan patrol"}}

User:
Open calculator

Output:
{{"skill":"calculator"}}

User:
Open VS Code

Output:
{{"skill":"vscode"}}

User:
What is on my screen

Output:
{{"skill":"vision","action":"screen_understanding"}}

If no skill matches, output:

{{"skill":"chat"}}

User:

{user_message}
"""

        response = self.ai.chat(
            prompt,
            history
        )

        try:

            return json.loads(response)

        except:

            return {
                "skill": "chat"
            }
