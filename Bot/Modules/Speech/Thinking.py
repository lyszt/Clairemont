import json

from google import genai
from pydantic import BaseModel

from Bot.Modules.Speech.Prompts import Prompts


class Command(BaseModel):
    command: str
    arg: str

class Thinking:
    def __init__(self, api_key, console):
        self.client = genai.Client(api_key=api_key)
        self.console = console

    def yes_no_decision(self, question: str):
        self.console.log(f"✨ Decidindo a questão: {question} ✨")
        response = self.client.models.generate_content(model="gemini-1.5-flash", contents=f"""
                  {question}
                  Answer the question above, and answer exclusively with "yes" or "no".
                   """)
        formatted_response = response.text.strip().lower()
        return formatted_response

    def naturalize(self, thought: str, context: str) -> str:
        self.console.log("✨ Cela peut être amélioré. Laisse-moi y réfléchir. ✨")

        response = self.client.models.generate_content(model="gemini-2.5-flash-preview-04-17", contents=f"""
        Tu es éditrice linguistique. Ta tâche est de réviser légèrement la [RÉPONSE DU BOT] afin de la rendre plus directe, naturelle et fluide vis-à-vis du [CONTEXTE DE L'UTILISATEUR].

        **Instructions :**
        1. Améliore le style pour qu’il soit plus naturel et fluide, tout en répondant directement à l’utilisateur.
        2. Ne modifie jamais le sens ou la personnalité du message d’origine.
        3. Si la réponse est déjà satisfaisante, rends-la telle quelle.
        4. Réponds uniquement avec le texte final révisé. N’ajoute aucun commentaire.
        5. Conserve la langue utilisée dans le message d’origine. Si le message de l’utilisateur est en anglais et la réponse en portugais, traduis la réponse dans la langue de l’utilisateur.

        [CONTEXTE DE L'UTILISATEUR] :
        {context}

        [RÉPONSE DU BOT À RÉVISER] :
        {thought}
        """)

        formatted_response = (response.text.strip("\n")).replace("\n", " ")
        return formatted_response

    def get_bot_command(self, user_message: str):
        """
        Analyzes the user's message to determine if it maps to a bot command.
        """
        self.console.log(f"✨ Checking for command in message: '{user_message}' ✨")

        # The prompt can be simplified slightly since the schema handles the structure
        prompt = f"""
         You are an AI assistant that determines if a user's request corresponds to one of your available commands and extracts the argument.

         Your available commands are:
         - "simplify": Simplifies a mathematical expression.
         - "fx": Generates a 2D plot of a function.
         - "fxy": Generates a 3D plot of a function.

         If no command is found, return "None" as the command.

         User's Message: "{user_message}"
         """


        try:
            response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            config={
                "response_mime_type": "application/json",
                "response_schema": Command,
            },
            contents=prompt
            )
            self.console.log(f"Command decision: {response.text}")
            command_obj = Command.model_validate_json(response.text)
            return command_obj.model_dump()
        except (json.JSONDecodeError, Exception) as e:
            self.console.log(f"Error decoding command from LLM: {e}")
            return {"command": "None", "arg": None}
