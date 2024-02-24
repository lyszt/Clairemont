import google.generativeai as genai


class GenerateText:
    def __init__(self):
        self.generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

    def talk(self, entry):
        model = genai.GenerativeModel(model_name="gemini-pro",
                                      generation_config=self.generation_config, safety_settings=self.safety_settings)
        response = model.generate_content(
            f"Você é mestre Sara, uma taverneira sensacional e super carismática. Responda no personagem à esta mensagem: {entry}")
        return response.text
