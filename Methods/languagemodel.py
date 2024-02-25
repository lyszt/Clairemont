import math
import os

import torch
from torch import autocast
from diffusers import StableDiffusionPipeline

#Stable Diffusion 1.5
MODEL_PATH = "CompVis/stable-diffusion-v1-4"
SAVE_PATH = "../temp"

if not os.path.exists(SAVE_PATH):
    os.mkdir(SAVE_PATH)
import google.generativeai as genai
import openai


class GenerateText:

    def run(self, entry, image_generation):
        prompt = self.gen_text(entry)
        if image_generation:
            url = self.gen_image(prompt)
            return prompt, url
        else:
            url = None
            return prompt, url

    def gen_image(self, entry):
        description = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens= 32,
            messages=[
                {"role": "system",
                 "content": "Write in english."},
                {"role": "user", "content": f""
                                            f"Based on the message '{entry}', make a very short description of the scene. "
                                            f"A blonde girl is there as well, so remember to mention."
                                            f"in detail for Stable Diffusion."}
            ]

        )
        description = f"Blonde girl, anime style, {description.choices[0].message.content}"
        response = openai.images.generate(
            model="dall-e-3",
            prompt=description,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    def gen_text(self, entry):
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
