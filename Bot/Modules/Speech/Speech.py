from google import genai

from Bot.Modules.Speech.Prompts import Prompts


class Speech:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def simpleSpeech(self, message : str) -> str:
        response = self.client.models.generate_content(model="gemini-2.5-flash-preview-04-17", contents=f"""
        {Prompts.self_concept}, {Prompts.chat_instructions} - MENSAGEM: {message}""")
        formatted_response = (response.text.strip("\n")).replace("\n", " ")
        return formatted_response
    def contextSpeech(self, message : str, context: str) -> str:
        return self.simpleSpeech(f"{message} - MENSAGENS ANTERIORES DO CHAT: {context}")
