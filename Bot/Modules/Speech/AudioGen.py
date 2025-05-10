import base64

import discord
import openai

import openai
import aiofiles
import discord
from openai import OpenAI

from Bot.Modules.Speech.Speech import Speech


class AudioGen:
    def __init__(self, api_key, console):
        self.api_key = api_key
        self.console = console



    async def gen_audio(self, interaction, context):
        try:
            completion = openai.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Você é Shadow Shock, um ator e aventureiro globalmente reconhecido. Praticamente uma popstar. Suas histórias são relatos de suas próprias experiências, sempre envolvendo:
                        - Dramas aleatórios, fofocas.
                        - Eventos improváveis onde sua sorte anormal resolve situações críticas.
                        - Um desfecho bem-sucedido, mesmo em cenários aparentemente impossíveis.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"Crie uma história curta e fictícia sobre você mesmo para adicionar à conversa que você está tendo com seus amigos. Fale em primeira pessoa. Contexto: {context}."
                    }
                ]
            )

            text = completion.choices[0].message.content.strip()
            client = OpenAI()
            with client.audio.speech.with_streaming_response.create(
                    model="gpt-4o-mini-tts",
                    voice="onyx",  # Better for rebellious tone
                    input=text,
                    instructions="Seja muito animado e meio sarcástico, como se fosse o protagonista.",
                    response_format="mp3"
            ) as response:
                response.stream_to_file("temp/speech.mp3")

            audio = discord.File("temp/speech.mp3")
            await interaction.channel.send(file=audio)

        except Exception as e:
           self.console.log(f"[ERROR] Couldn't generate audio. {e}")

