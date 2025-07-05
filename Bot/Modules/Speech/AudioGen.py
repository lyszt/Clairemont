import discord
import openai
from openai import OpenAI
from pydub import AudioSegment

class AudioGen:
    def __init__(self, api_key, console):
        openai.api_key = api_key
        self.console = console
        self.client = OpenAI(api_key=api_key)

    async def generate_audio(self, message, context):
        try:
            self.console.log("✨ Sara réfléchit à la meilleure réponse technique... ✨")

            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Tu es Sara Clairemont, cheffe de projet ingénieure chez Lygon, responsable du Litessera Project. "
                            "Tu parles français avec précision et clarté, en alliant rigueur scientifique et bienveillance. "
                            "Ton but est d’apporter une réponse technique concise tout en gardant un ton encourageant et collaboratif."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"L’utilisateur {message.author.display_name} vient de dire : « {message.content} ». "
                            "Réponds-lui de manière claire et professionnelle, propose une solution ou une piste d’amélioration, "
                            "et termine sur une note positive. Sois concise et didactique."
                        )
                    }
                ]
            )

            texte = completion.choices[0].message.content.strip()
            self.console.log(f"Pensée vocale de Sara : {texte}")

            chemin_audio_brut = "temp/voix_brute.mp3"
            chemin_audio_final = "temp/voix_traitée.mp3"

            with self.client.audio.speech.with_streaming_response.create(
                model="tts-1-hd",
                voice="fleur",
                instructions="Parle sur un ton professionnel, clair et rassurant, comme une ingénieure cheffe de projet.",
                input=texte,
                response_format="mp3"
            ) as response:
                response.stream_to_file(chemin_audio_brut)

            self.console.log("Application de l’effet de réverbération légère...")

            son = AudioSegment.from_mp3(chemin_audio_brut)
            reverb = son.overlay(son - 8, position=50)
            reverb = reverb.overlay(son - 12, position=100)
            reverb.export(chemin_audio_final, format="mp3")

            fichier_audio = discord.File(chemin_audio_final, filename="sara_litessera.mp3")
            await message.channel.send(file=fichier_audio)

        except Exception as e:
            self.console.log(f"[ERREUR] Impossible de générer l’audio de Sara : {e}")
