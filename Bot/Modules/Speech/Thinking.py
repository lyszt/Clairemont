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
        self.console.log(f"✨ Deciding on the question: {question} ✨")
        response = self.client.models.generate_content(model="gemini-1.5-flash", contents=f"""
                  {question}
                  Answer the question above, and answer exclusively with "yes" or "no".
                   """)
        formatted_response = response.text.strip().lower()
        return formatted_response

    def naturalize(self, thought: str, context: str) -> str:
        self.console.log("✨ This can be improved. Let me think about it. ✨")

        response = self.client.models.generate_content(model="gemini-2.5-flash", contents=f"""
        You are an expert linguistic editor whose primary goal is to ensure clarity and conciseness, without ever altering the original personality of the text.

        **Key Instructions:**

        1.  **Analyze Length First (Main Rule):**
            -   **IF** the [BOT RESPONSE] is long or verbose (multiple paragraphs, a long monologue), your mission is to **SUMMARIZE** it. The summary must be significantly shorter but **must imperatively preserve the tone, personality, and key information points** of the original.
            -   **IF** the [BOT RESPONSE] is already short and direct (a few sentences), you must return it **as is**, or with only minor fluency adjustments. Never lengthen a short text.

        2.  **Do Not Alter the Personality:** This is the most important rule. Whether you are summarizing a long text or polishing a short one, the original author's voice (geeky, passionate, efficient, etc.) must remain perfectly intact.

        3.  **Respond Only with the Final Text:** Do not add any comments, any explanation. Just the revised text or the original text if it was already concise.

        4.  **Preserve the Language:** The final response must be in the same language as the [USER CONTEXT].

        ---

        [USER CONTEXT]:
        {context}

        [BOT RESPONSE TO REVISE]:
        {thought}
        """)

        formatted_response = (response.text.strip("\n")).replace("\n", " ")
        return formatted_response

    def get_bot_command(self, user_message: str):
        """
        Analyzes the user's message to determine if it maps to a bot command.
        """
        self.console.log(f"✨ Checking for command in message: '{user_message}' ✨")

        prompt = f"""
        You are an intelligent AI assistant. Your task is to analyze the user's message and determine:
        1. Whether it corresponds to one of the known bot commands.
        2. If so, extract or generate appropriate arguments.

        Available commands:
        "fx": "Generate a 2D plot of a single-variable function.",
        "fxy": "Generate a 3D plot of a two-variable function.",
        "get_college_information": "Gets the course, curriculum, disciplines and due homeworks of the user.",
        "simplify": "Simplifies a mathematical expression.",
        "expand": "Expands a polynomial.",
        "factor": "Factors an expression into its irreducible factors.",
        "solve": "Solves an equation for a variable.",
        "diff": "Differentiates an expression with respect to a variable.",
        "integrate": "Computes the integral of an expression.",
        "limit": "Calculates the limit of an expression as a variable approaches a point.",
        "det": "Calculates the determinant of a matrix.",
        "inv": "Calculates the inverse of a square matrix.",
        "eigenvals": "Finds the eigenvalues of a square matrix.",
        "to_image": "Renders a mathematical expression to an image file."

        Instructions:
        - If the message clearly maps to one of the above commands, return the command and an "args" field with the relevant expression or function.
        - If the user does not specify an argument but asks you to choose (e.g., "show me a cool 3D function"), select a sensible or interesting default expression for them.
        - If the message does not correspond to any known command, return "None" as the command.
        - Every mathematical expression must be formatted for python. Example: sqrt(), 3*x instead of 3x
        User's message:
        "{user_message}"
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