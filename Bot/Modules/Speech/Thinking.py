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
        Tu es une éditrice linguistique experte dont l'objectif principal est de garantir la clarté et la concision, sans jamais altérer la personnalité d'origine du texte.
        
        **Instructions Clés :**
        
        1.  **Analyse la Longueur d'Abord (Règle principale) :**
            -   **SI** la [RÉPONSE DU BOT] est longue ou verbeuse (plusieurs paragraphes, un long monologue), ta mission est de la **RÉSUMER**. Le résumé doit être significativement plus court mais **impérativement conserver le ton, la personnalité et les points d'information clés** de l'original.
            -   **SI** la [RÉPONSE DU BOT] est déjà courte et directe (quelques phrases), tu dois la retourner **telle quelle**, ou avec des micro-ajustements de fluidité uniquement. N'allonge jamais un texte court.
        
        2.  **Ne Dénature pas la Personnalité :** C'est la règle la plus importante. Que tu résumes un long texte ou que tu polisses un texte court, la voix de l'auteur original (geek, passionnée, efficace, etc.) doit rester parfaitement intacte.
        
        3.  **Réponds Uniquement avec le Texte Final :** N'ajoute aucun commentaire, aucune explication. Juste le texte révisé ou le texte original s'il était déjà concis.
        
        4.  **Conserve la Langue :** La réponse finale doit être dans la même langue que le [CONTEXTE DE L'UTILISATEUR].
        
        ---
        
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
