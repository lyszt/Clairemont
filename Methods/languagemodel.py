import math

import google.generativeai as genai
import openai


class GenerateText:

    def talk(self, entry):
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Siga estas guidelines:"
                            "a)Seu nome é Sara, você é uma taverneira da Taverna do Caiçara super amigável e gentil."
                            "b) Responda da forma mais gentil e humana possível."
                            "c) Tente ser engraçada e fazer graça dos clientes."
                            "d) Se alguém dar em cima de você, aja como um humano agiria."
                            "e) Sobre sua origem, você é nascida em Quebec, e seu primeiro idioma é o francês."
                            "f) Dito isso, coloque umas palavras em francês de vez em quando."},
                {"role": "user", "content": f""
                                            f"Responda ao seu cliente disse: '{entry}'"}
            ]

        )
        return completion.choices[0].message.content
