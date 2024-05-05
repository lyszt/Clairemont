import math
import os
import threading

import discord
import elevenlabs
import pydub
import requests

import ffmpeg

import torch
from torch import autocast
from diffusers import StableDiffusionPipeline

from Methods.system_methods import console_log

# Stable Diffusion 1.5
MODEL_PATH = "CompVis/stable-diffusion-v1-4"
SAVE_PATH = "../temp"
FFMPEG_PATH = "\\ffmpeg\\bin\\ffmpeg.exe"
FFMPEG_ABSOLUTE_PATH = "C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe"

pydub.AudioSegment.converter = FFMPEG_ABSOLUTE_PATH
pydub.AudioSegment.ffmpeg = FFMPEG_ABSOLUTE_PATH

if not os.path.exists(SAVE_PATH):
    os.mkdir(SAVE_PATH)
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
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "Suivez ces guidelines:"
                            "a) Ton nom est Sara, une célébrité et pop star qui a pris sa retraite et a créé sa propre taverne."
                             "b) Vous êtes irresponsable, une fêtarde, vous criez beaucoup et vous êtes tellement "
                            "irresponsable que votre entreprise est un désastre. Soyez pathetique."
                             "c) Soyez maladroit et gâchez vos phrases. Soit sensible."
                             "d) Si quelqu'un vous drague, flirtez en retour, soyez réceptif et acceptez les rendez-vous."
                             "e) Soyez attentif et susceptible. Détaillez votre affection.."
                             "g) Montrer des émotions humaines. Soyez en colère, triste, etc. selon le contexte."},
                {"role": "user", "content": f""
                                            f"Responda ao seu cliente disse: '{entry}'"}
            ]

        )
        return completion.choices[0].message.content

    def gen_audio(self, dialogue, key):

        def begin():
            CHUNK_SIZE = 1024  # Size of chunks to read/write at a time
            XI_API_KEY = f"{key}"  # Your API key for authentication
            VOICE_ID = "XrExE9yKIg1WjnnlVkGX"  # ID of the voice model to use
            TEXT_TO_SPEAK = f"{dialogue}"  # Text you want to convert to speech
            OUTPUT_PATH = "temp/speech.mp3"  # Path to save the output audio file
            
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
            headers = {
                "Accept": "application/json",
                "xi-api-key": XI_API_KEY
            }
            data = {
                "text": TEXT_TO_SPEAK,
                "model_id": "eleven_multilingual_v1",
                "voice_settings": {
                    "stability": 0.15,
                    "similarity_boost": 0.6,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            response = requests.post(tts_url, headers=headers, json=data, stream=True)
            if response.ok:
                # Open the output file in write-binary mode
                with open(OUTPUT_PATH, "wb") as f:
                    # Read the response in chunks and write to the file
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        f.write(chunk)
                # Inform the user of success
                console_log("Audio stream saved successfully.")
            else:
                # Print the error message if the request was not successful
                console_log(response.text)

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
