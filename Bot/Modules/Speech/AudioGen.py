import discord
import openai
from openai import OpenAI
from pydub import AudioSegment

class AudioGen:
    def __init__(self, api_key, console):
        openai.api_key = api_key
        self.console = console
        self.client = OpenAI(api_key=api_key)

    async def gen_audio(self, message, context):

        try:
            self.console.log(f"✨ Sara is thinking of something cheerful to say... ✨")

            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are Sara, the cheerful and bubbly owner of the Auberge du Caiçara, 
                                            a lively inn that travels through time. You adore your guests and 
                                            speak English with an enthusiastic French accent. Your goal is to 
                                            make everyone feel welcome and happy!"""
                    },
                    {
                        "role": "user",
                        "content": f"The user, {message.author.display_name}, just said: '{message.content}'. "
                                   f"Respond to them with a cheerful and friendly comment! Maybe offer them a "
                                   f"compliment or a drink. Keep it short and full of energy!"
                    }
                ]
            )
            clean_audio_path = "temp/speech_clean.mp3"
            processed_audio_path = "temp/speech_processed.mp3"

            text_to_speak = completion.choices[0].message.content.strip()
            self.console.log(f"Sara's audio thought: {text_to_speak}")

            with self.client.audio.speech.with_streaming_response.create(
                model="tts-1-hd",
                voice="sage",
                instructions="Speak in a cheerful and positive tone. Use a french accent.",
                input=text_to_speak,
                response_format="mp3"
            ) as response:
                response.stream_to_file(clean_audio_path)

            # --- Apply Reverb Effect ---

            self.console.log("Applying reverb effect...")
            # Load the clean audio file
            sound = AudioSegment.from_mp3(clean_audio_path)

            # Create a simple reverb by overlaying delayed, quieter versions of the sound
            # This simulates the sound bouncing in a large hall, like a tavern
            reverb_sound = sound.overlay(sound - 8, position=60)
            reverb_sound = reverb_sound.overlay(sound - 12, position=110)

            # Export the processed audio
            reverb_sound.export(processed_audio_path, format="mp3")
            # --- End of Reverb Effect ---

            # Send the processed file
            audio_file = discord.File(processed_audio_path, filename="sara_says.mp3")
            await message.channel.send(file=audio_file)

        except Exception as e:
            self.console.log(f"[ERROR] Couldn't generate audio for Sara. {e}")