import re

from google import genai

from Bot.Modules.Speech.Prompts import Prompts
from Bot.Modules.Speech.Thinking import Thinking

# Define Discord's character limit as a constant
DISCORD_CHAR_LIMIT = 2000

def strip_markdown(text: str) -> str:
    """
    Cette fonction nettoie le texte de ses caractères Markdown les plus courants.
    """
    # Enlève les astérisques, tirets bas et anti-quotes (gras, italique, code)
    text = re.sub(r'[\*_`]', '', text)
    # Enlève les titres (lignes commençant par #)
    text = re.sub(r'^\s*#+\s*', '', text, flags=re.MULTILINE)
    return text


class Speech:
    def __init__(self, api_key, console):
        self.client = genai.Client(api_key=api_key)
        self.api_key = api_key
        self.console = console

    def simpleSpeech(self, message: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.5-flash-preview-04-17",
            contents=f"{Prompts.self_concept}, {Prompts.chat_instructions} - MESSAGE: {message}"
        )
        formatted_response = (response.text.strip("\n")).replace("\n", " ")
        plain_text_response = strip_markdown(formatted_response)

        return plain_text_response[:DISCORD_CHAR_LIMIT]

    def contextSpeech(self, message: str, context: str) -> str:
        initial_speech = self.simpleSpeech(f"MESSAGE: {message} - MESSAGES ANTERIEURES: {context}")
        final_speech = Thinking(self.api_key, self.console).naturalize(initial_speech, context)

        return final_speech[:DISCORD_CHAR_LIMIT]