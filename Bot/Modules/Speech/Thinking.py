from google import genai

from Bot.Modules.Speech.Prompts import Prompts


class Thinking:
    def __init__(self, api_key, console):
        self.client = genai.Client(api_key=api_key)
        self.console = console

    def naturalize(self, thought : str, context: str) -> str:
        self.console.log("✨ This could be better. Let me rethink it. ✨")
        response = self.client.models.generate_content(model="gemini-2.0-flash", contents=f"""
        Deixe essa mensagem mais natural para um ambiente de chat virtual
        e retorne-a. Não comente mais nada. Responda apenas com a frase melhorada.
        Deixe ela mais natural para o contexto apresentado e as mensagens passadas dos usuários.
        MENSAGEM : {thought}
        MENSAGENS PASSADAS: {context}
        """)
        formatted_response = (response.text.strip("\n")).replace("\n", " ")
        return formatted_response

