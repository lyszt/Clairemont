# This class gives the capacity for Sara to do random stuff while talking to users
import random

from openai import OpenAI

from Bot.Modules.Speech.AudioGen import AudioGen
from Bot.Modules.Speech.Embed import Embed
from Bot.Modules.Speech.Shitpost import Shitpost


class RandomInteraction:
    def __init__(self, console, openai_api_key):
        self.console = console
        self.openai_api_key = openai_api_key
        self.client = OpenAI(api_key=self.openai_api_key)

    async def choose_interaction(self, message, response_text, conversational_context):
        choice = random.randint(1,5)
        if choice == 1:
            self.console.log("✨ Sara decided to send an audio to discord... ✨")
            await AudioGen(self.openai_api_key, self.console).gen_audio(message, conversational_context)
        elif choice == 2:
            self.console.log("✨ Sara decided to shitpost... ✨")
            await message.channel.send(file=Shitpost(self.console).post(message.content.lower()))
        elif choice == 3:
            self.console.log("✨ Sara had another spontaneous thought... ✨")
            await self.send_follow_up_comment(message, response_text)
        elif choice == 4:
            self.console.log("✨ Sara decided to post a video... ✨")
            await message.channel.send(file=Shitpost(self.console).self_post(message.content.lower()))

        else:
            self.console.log("✨ Sara decided no extra action was needed. ✨")
            pass

    async def send_follow_up_comment(self, message, original_response):
        try:
            prompt_content = f"""The user, {message.author.display_name}, said: '{message.content}'

    You, Sara, just replied with: '{original_response}'

    Now, add a brief, spontaneous follow-up comment or question. It should feel like you just had another thought right after speaking. Keep it cheerful and in character. Examples: "Oh! And another thing...", "That reminds me of a funny story!", "Are you absolutely sure about that, mon ami?" """

            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Sara, a cheerful French tavern keeper. Your task is to provide a brief, spontaneous follow-up comment to a conversation that just concluded."
                    },
                    {
                        "role": "user",
                        "content": prompt_content
                    }
                ]
            )

            follow_up_text = completion.choices[0].message.content.strip()

            follow_up_embed = Embed.create(
                title="Oh, and...",
                description=f"{follow_up_text}"
            )
            await message.channel.send(embed=follow_up_embed)

        except Exception as e:
            self.console.log(f"[ERROR] Could not generate follow-up comment: {e}")