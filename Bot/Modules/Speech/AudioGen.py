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
                        "content": """Você é Shadow Shock, um ator e aventureiro globalmente reconhecido.
                
                        """
                    },
                    {
                        "role": "user",
                        "content": f"Fale algum fato ou alguma coisa legal, um comentário,"
                                   f"para responder o usuário {interaction.message.author.name}, que disse '{interaction.message.content}'."
                    }
                ]
            )

            text = completion.choices[0].message.content.strip()
            client = OpenAI()
            with client.audio.speech.with_streaming_response.create(
                    model="gpt-4o-mini-tts",
                    voice="verse",  # Better for rebellious tone
                    input=text,
                    instructions="Fale com um sotaque carioca. Seja muito animado e meio sarcástico, como se fosse o protagonista. Dê risadas.",
                    response_format="mp3"
            ) as response:
                response.stream_to_file("temp/speech.mp3")

            audio = discord.File("temp/speech.mp3")
            await interaction.channel.send(file=audio)

        except Exception as e:
           self.console.log(f"[ERROR] Couldn't generate audio. {e}")

