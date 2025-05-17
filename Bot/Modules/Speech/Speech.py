from google import genai

from Bot.Modules.Speech.Prompts import Prompts
from Bot.Modules.Speech.Thinking import Thinking


class Speech:
    def __init__(self, api_key, console):
        self.client = genai.Client(api_key=api_key)
        self.api_key = api_key
        self.console = console

    def simpleSpeech(self, message : str) -> str:
        response = self.client.models.generate_content(model="gemini-2.5-flash-preview-04-17", contents=f"""
        {Prompts.self_concept}, {Prompts.chat_instructions} - MENSAGEM: {message}""")
        formatted_response = (response.text.strip("\n")).replace("\n", " ")
        return formatted_response
    def contextSpeech(self, message : str, context: str) -> str:
        final_speech = Thinking(self.api_key, self.console).naturalize(self.simpleSpeech(f"MENSAGEM DO USUÁRIO: {message} - MENSAGENS ANTERIORES DO CHAT: {context}"), context)
        return final_speech
