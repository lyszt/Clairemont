from google import genai

from Bot.Modules.Speech.Prompts import Prompts


class Thinking:
    def __init__(self, api_key, console):
        self.client = genai.Client(api_key=api_key)
        self.console = console

    def naturalize(self, thought : str, context: str) -> str:
        self.console.log("✨ This could be better. Let me rethink it. ✨")
        response = self.client.models.generate_content(model="gemini-2.5-flash-preview-04-17", contents=f"""
        Essa mensagem responde apropriadamente a fala do usuário? Edite a resposta de forma
        que ela se direcione à mensagem do usuario e retorne-a. Não comente mais nada. Responda apenas com a frase melhorada.
        MENSAGEM : {thought}
        """)
        formatted_response = (response.text.strip("\n")).replace("\n", " ")
        return formatted_response

