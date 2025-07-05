# Cette classe donne à Sara la capacité de faire des choses aléatoires pendant qu'elle parle avec les utilisateurs
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
        choice = random.randint(1,1)
        if choice == 1:
            self.console.log("✨ Sara a décidé d’envoyer un message audio sur Discord... ✨")
            await AudioGen(self.openai_api_key, self.console).generate_audio(message, conversational_context)
        elif choice == 2:
            self.console.log("✨ Sara a décidé de faire un peu d’humour absurde... ✨")
            await message.channel.send(file=Shitpost(self.console).post_video(message.content.lower()))
        elif choice == 3:
            self.console.log("✨ Sara a eu une autre pensée spontanée... ✨")
            await self.send_follow_up_comment(message, response_text)
        elif choice == 4:
            self.console.log("✨ Sara a décidé de poster une vidéo... ✨")
            await message.channel.send(file=Shitpost(self.console).self_post(message.content.lower()))
        elif choice == 5:
            self.console.log("✨ Sara a décidé de faire du shitposting... ✨")
            await message.channel.send(Shitpost(self.console).post_curl())
        else:
            self.console.log("✨ Sara a estimé qu’aucune action supplémentaire n’était nécessaire. ✨")
            pass

    async def send_follow_up_comment(self, message, original_response):
        try:
            prompt_content = f"""L'utilisateur, {message.author.display_name}, a dit : '{message.content}'

    Toi, Sara, viens de répondre : '{original_response}'

    Maintenant, ajoute un bref commentaire ou une question spontanée. Il doit donner l'impression d'une pensée qui t’est venue juste après avoir parlé. Reste enjouée et dans ton personnage. Exemples : "Oh ! Et une autre chose...", "Ça me rappelle une histoire amusante !", "Tu es vraiment sûr·e de ça, mon ami ?" """

            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es Sara, une ingénieure française vive et curieuse. Ton rôle est d’ajouter un bref commentaire de suivi, spontané, à une conversation qui vient de se terminer."
                    },
                    {
                        "role": "user",
                        "content": prompt_content
                    }
                ]
            )

            follow_up_text = completion.choices[0].message.content.strip()

            follow_up_embed = Embed.create(
                title="Oh, et aussi...",
                description=f"{follow_up_text}"
            )
            await message.channel.send(embed=follow_up_embed)

        except Exception as e:
            self.console.log(f"[ERREUR] Impossible de générer un commentaire de suivi : {e}")
