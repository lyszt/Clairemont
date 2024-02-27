import math
import os
import threading

import discord
import elevenlabs
import pydub
import ffmpeg

import torch
from torch import autocast
from diffusers import StableDiffusionPipeline

# Stable Diffusion 1.5
MODEL_PATH = "CompVis/stable-diffusion-v1-4"
SAVE_PATH = "../temp"
FFMPEG_PATH = "\\ffmpeg\\bin\\ffmpeg.exe"
FFMPEG_ABSOLUTE_PATH = "C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe"

pydub.AudioSegment.converter = FFMPEG_ABSOLUTE_PATH
pydub.AudioSegment.ffmpeg = FFMPEG_ABSOLUTE_PATH

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
            max_tokens=32,
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
                            "d) Se alguém dar em cima de você, flerte de volta."
                            "e) Sobre sua origem, você é nascida em Quebec."
                            "f) Seus gostos e interesses: Doctor Who, Jazz, Artes Marciais"
                            "g) Você odeia: Clientes mal-educados, pessoas da Jambônia"
                            "h) Dito isso, se aparecer alguém da Jambônia, fique brava e se recuse a atendê-lo. Chame os seguranças e fique apavorada."
                            "i) Demonstre emoções humanas. Fique brava, triste, etc dependendo do contexto."
                            "j) Não pergunte se precisa de mais alguma coisa."},
                {"role": "user", "content": f""
                                            f"Responda ao seu cliente disse: '{entry}'"}
            ]

        )
        return completion.choices[0].message.content

    def gen_audio(self, dialogue):

        def begin():
            audio = elevenlabs.generate(
                text=dialogue,
                voice="Sally",
                model="eleven_multilingual_v2"
            )
            elevenlabs.save(audio, "temp/speech.mp3")

        def mix():
            speech = pydub.AudioSegment.from_mp3("temp/speech.mp3")
            ambience = pydub.AudioSegment.from_mp3("Dialogues/cantina_ambience.mp3")
            combined = speech.overlay(ambience)
            combined.export("temp/edited_speech.mp3", format='mp3')

        produce = threading.Thread(target=begin)
        mix = threading.Thread(target=mix)
        produce.start()
        produce.join()
        mix.start()
        mix.join()

    async def send_audio(self, interaction):
        audio = discord.File("temp/edited_speech.mp3")
        await interaction.channel.send(file=audio)
