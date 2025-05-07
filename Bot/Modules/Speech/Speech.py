from google import genai

from Bot.Modules.Speech.Prompts import Prompts


class Speech:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def simpleSpeech(self, message : str, context: str) -> str:
        response = self.client.models.generate_content(model="gemini-2.0-flash-lite", contents=f"""
        {Prompts.self_concept}, {Prompts.chat_instructions} - MENSAGEM: {message}   - MENSAGENS ANTERIORES DO CHAT: {context}""")
        return response.text
