from google import genai

from Bot.Modules.Speech.Prompts import Prompts


class Thinking:
    def __init__(self, api_key, console):
        self.client = genai.Client(api_key=api_key)
        self.console = console

    def naturalize(self, thought: str, context: str) -> str:
        self.console.log("✨ This could be better. Let me rethink it. ✨")

        response = self.client.models.generate_content(model="gemini-2.5-flash-preview-04-17", contents=f"""
        You are an editor. Your job is to lightly edit the [BOT'S RESPONSE] to make it a more direct and natural-sounding reply to the [USER'S CONTEXT].

        **Instructions:**
        1.  Focus on improving the flow and ensuring the response directly addresses the user.
        2.  Do NOT change the core meaning or personality of the bot's response.
        3.  If the response is already good, return it unchanged.
        4.  Respond ONLY with the final, improved text. Do not add comments.
        5. Keep it in the language in which it was spoken. If the user speaks english and the response is in portuguese, translate it.

        [USER'S CONTEXT]:
        {context}

        [BOT'S RESPONSE TO EDIT]:
        {thought}
        """)

        formatted_response = (response.text.strip("\n")).replace("\n", " ")
        return formatted_response