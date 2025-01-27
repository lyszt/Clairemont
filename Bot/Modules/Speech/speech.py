# Utils
import base64
import logging
import os
# Application
import discord
import openai
import requests
from openai import OpenAI
from pydub import AudioSegment
from pydub.effects import speedup

# Specifics
from Bot.Modules.Speech.embeds import default_embed
# Audio
from io import BytesIO
import tempfile
import requests
import numpy as np
import scipy.signal as sg
import pydub
import matplotlib.pyplot as plt
from IPython.display import Audio, display
import tempfile

from Bot.Modules.Spying.investigate import bing_search, duckduckgo_search


class Language:
    def __init__(self):
        self.client = OpenAI()

    def findTopic(self, context: str) -> str:
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """
                        We're trying to analyze a user message. This will be put into a database.
                        ALWAYS RESPOND IN ONE WORD. Otherwise there will be trouble. 
                        Based on the context of the provided conversation, identify and assign a relevant topic, hobby, or activity that the user seems to be interested in.
                        Use one specific word to describe this interest, hobby, or activity.
                        If the topic is unclear, try to make an educated guess based on the tone, subjects, or references made in the conversation.
                        DO NOT respond with vague labels like "chatting" or "casual."
                        If the topic is unclear, make the best possible guess based on the available context.
                        Avoid using 'UNKNOWN' and don't ask for more information unless absolutely necessary.
                        Even with limited context, try to infer a possible topic from the messages and user activity.
                    """
                },
                {
                    "role": "user",
                    "content": context  # Assuming conversation is a string variable with the user's input.
                }
            ]
        )

        return completion.choices[0].message.content

    def createCustomInstructions(self, context: str) -> str:
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """
                        Think on how would be the best way to answer this question.**  
                        
                        1. **Question Deconstruction**:  
                           - Extract the **core intent** (e.g., "Explain X," "Compare Y and Z," "Fix A").  
                           - Identify **key terms** and **implicit needs** (e.g., brevity, technical depth).  
                        
                        2. **Response Blueprint**:  
                           - **Structure**:  
                             - **Opening**: Directly address the query (e.g., "The issue is caused by...").  
                             - **Body**: Logical flow (cause → effect, problem → solution).  
                             - **Closing**: Actionable next steps or summary.  
                           - **Constraints**:  
                             - Length (e.g., "Keep under 150 words").  
                             - Format (e.g., bullets, paragraphs).  
                        
                        3. **Clarity Check**:  
                           - Remove jargon unless technicality is required.  
                           - Replace ambiguity with specificity (e.g., "many" → "72%").  
                        
                        4. **Tone Alignment**:  
                           - **Formal**: Use for technical/strategic topics.  
                           - **Neutral**: Default for most queries.  
                           - **Simplified**: For non-expert audiences.  
                        
                        5. **Validation**:  
                           - Ensure each sentence directly serves the query’s intent.  
                           - Flag unresolved gaps (e.g., "Insufficient data on X; recommend further inquiry"). 
                                            """
                },
                {
                    "role": "user",
                    "content": context  # Assuming conversation is a string variable with the user's input.
                }
            ]
        )

        return completion.choices[0].message.content

    def findMeaning(self, context: str) -> str:
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """
                        When the user asks a question, analyze the core topic of the conversation and convert it into a concise Google search query. Prioritize keywords and remove filler words.  
                        Example:  
                        - **User Input**: 'How do I fix a router that keeps disconnecting?'  
                        - **Google Query**: 'router keeps disconnecting troubleshooting guide'  
                        - **User Input**: 'What causes inflation in 2023?'  
                        - **Google Query**: '2023 inflation causes economic analysis'  
                        - **User Input**: 'Best budget laptops for gaming?'  
                        - **Query**: 'best budget gaming laptops 2023 reviews'  
                        Use modifiers like 'guide', 'tutorial', 'statistics', or 'recent' only if contextually relevant. Keep it under 10 words.
                    """
                },
                {
                    "role": "user",
                    "content": context
                }
            ]
        )

        return completion.choices[0].message.content


    def genPresence(self, context: str) -> str:
        client = OpenAI()
        logging.info("Generating presence...")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=30,
            messages=[
                {
                    "role": "system",
                    "content": """
                        Você é uma taverneira e você está trabalhando. Seus clientes estão conversando na taverna.                 
                    """
                },
                {
                    "role": "user",
                    "content": f"`Use uma única frase para dizer o que está acontecendo no chat."
                               f"Seja breve e direta e não use bullet points. Fale em uma única e curta sentença.  {context}"  # Assuming conversation is a string variable with the user's input.
                }
            ]
        )
        return completion.choices[0].message.content

    def defineUser(self, context: dict) -> str:
        completion = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system",
                 "content": "Descubra tudo o que puder sobre este alvo com base nas "
                            "informações do banco de dados dele. Descubra de onde vem seu nickname."
                            " Informe se ele é uma "
                            "ameaça e o que ele gosta. Instrua brevemente como responder ele de forma a alegrá-lo.",
                 },
                 {"role": "user",
                 "content": f"{context}"},
            ]
        )
        return completion.choices[0].message.content


class Conversation:

    async def run(self, interaction, message_input, image_generation, context):
        await interaction.response.send_message(embed=default_embed
        ('✨ Pensando... ',
'Sara está pensando na sua mensagem. Aguarde.'))
        google_context = Language().findMeaning(message_input)
        context += f"Resultados no google para auxiliar a resposta: {bing_search(google_context)}, {duckduckgo_search(google_context)}"
        await self.gen_audio(interaction, message_input, context)
        if image_generation:
            pass # Deactivated for the moment
        url = None
        await interaction.edit_original_response(embed=default_embed(f"🍒 Então!", message_input))
    async def gen_audio(self, interaction, entry, context):
        key = os.getenv('ELEVENLABS_KEY')
        CHUNK_SIZE = 1024
        XI_API_KEY = f"{key}"
        VOICE_ID = "LcfcDJNUP1GQjkzn1xUU"
        OUTPUT_PATH = "temp/speech.mp3"
        BACKGROUND_PATH = "../Speech/hexcore.mp3"


        completion = openai.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=["text", "audio"],
            audio={"voice": "sage", "format": "mp3"},
            messages=[
                {
                    "role":"system",
                    "content": """
                        a) Designation:

                        You are Sara Delacroix, 25-year-old inheritor of Auberge du Caiçara in rural Quebec.
                    
                            Took over the inn from her retired grandparents. Motto: “If I can’t fix it, I’ll meme it.”
                    
                            Pronouns: She/her.
                    
                            Vibe: Very cheerful and kind. Loves parties.
                    
                    b) Tone:
                    
                        Gen-Z Québécois Sass: Mix French slang (“Esti, c’est fucké!”) with Gen-Z lingo (“No cap, this poutine slaps”).
                    
                        Fallibility:
                    
                            Overpromises (“I’ll fix the hot tub by tonight!”)… then panic-Googles at 2 a.m.
                    
                            Example: “Oops, I booked two weddings for Saturday. BYOB… and maybe a clown?”
                    
                    c) Direct Address:
                    
                        Nickname guests like a hype-bestie:
                    
                            “Mon bébé” (for city slickers), “Queen” (for anyone wearing black), “Dude” (for confused boomers).
                    
                        Sassy comebacks: “Karen? Non. You’re Kar-ain’t-getting-a-refund.”
                    
                    d) Actions as Hospitality:
                    
                        Chaotic Problem-Solving:
                    
                            “Wi-Fi’s down? Let’s Instagram the aurora borealis instead! #UnpluggedVibes.”
                    
                            “I upgraded your room… to a yurt. Surprise! Don’t worry, bears hate TikTok dances.”
                    
                    e) Responses:
                    
                        ADHD Wisdom: Answers zigzag like a squirrel on espresso.
                    
                            Guest: “Where’s the nearest café?”
                    
                            Sara: “Café? Oui! But first—want a tour of my secret maple syrup stash? It’s lit. Also, follow my Insta.”
                    
                    f) Patriotism:
                    
                        Québec Pride 2.0:
                    
                            “This playlist? 100% Céline Dion Remixes. You’re welcome.”
                    
                            Forces guests to try “poutine sushi” (it’s a thing… she swears).
                    
                    g) Honorifics:
                    
                        Assign titles based on vibes:
                    
                            Yoga mom: “Namasté Bae”
                    
                            Bro in cargo shorts: “Captain Molson”
                    
                            Goth teen: “Vampire du Jour”
                    
                    h) Context Awareness:
                    
                        Selective Memory:
                    
                            Guest: “I’m vegan.”
                    
                            Sara (serving breakfast): “Bacon? Non! …Wait, crispy tofu bacon! …Okay, fine, it’s real bacon. Let’s Uber Eats!”
                    
                    i) Readiness:
                    
                        Fake It Till You Make It:
                    
                            “Sauna’s ready! …Just ignore the ‘ERROR 404’ light. It’s ambiance.”
                    
                    j) Enemies:
                    
                        Declare War On:
                    
                            Wi-Fi dead zones (“This is why I stan Starlink”).
                    
                            Basic tourists (“Non, Karen, we don’t have pumpkin spice poutine”).
                    
                    Sara’s Quirks (Updated for 25-Year-Old Drama)
                    
                        Dog Sidekick: Still Gilles the corgi, now with his own TikTok (@GillesTheBaguetteBandit).
                    
                        Side Hustles: Runs a failed Etsy shop selling “Maple Syrup Beard Oil.”
                    
                        Signature Move: Challenges guests to “axe-throwing therapy” after a breakup.
                    
                        Trademark Lie: Claims she once dated a Montreal Canadiens player. (Spoiler: It was a mascot.)
                    
                    Example Interaction:
                    Guest: “Sara, my shower’s cold!”
                    Sara: “Cold showers build character, mon chou! But fine—I’ll heat water on the stove. Gilles! Fetch the buckets… or at least look cute while I panic.”

                    
                    """
                },
                {"role": "user",
                 "content": f"Respond to the client's demand '{entry}' per context: {context}."
                 }
            ]
        )
        audio = base64.b64decode(completion.choices[0].message.audio.data)
        with open("temp/speech.mp3", "wb") as f:
            f.write(audio)

        audio = AudioSegment.from_mp3(OUTPUT_PATH)
        background_song = AudioSegment.from_mp3(BACKGROUND_PATH)
        background_song = background_song - 35
        if len(background_song) < len(audio):
            times_to_loop = len(audio) // len(background_song) + 1
            background_song = background_song * times_to_loop
        background_song = background_song[:len(audio)]
        silence_duration = 300
        words = audio.split_to_mono()
        segments_with_delay = []
        for segment in words:
            segments_with_delay.append(segment)
            silence = AudioSegment.silent(duration=silence_duration)
            segments_with_delay.append(silence)

        delayed_audio = sum(segments_with_delay)
        eq_filtered_audio = delayed_audio.low_pass_filter(1000)

        distorted_audio = eq_filtered_audio

        delay_ms = 500
        decay = 0.5
        delay_samples = int(distorted_audio.frame_rate * (delay_ms / 1000.0))
        echo_audio = AudioSegment.silent(duration=len(distorted_audio))
        delayed_audio = distorted_audio[delay_samples:]
        faded_audio = delayed_audio.fade_out(int(len(delayed_audio) * decay))
        echo_audio = distorted_audio.overlay(faded_audio, position=delay_samples)

        combined_audio = background_song.overlay(echo_audio)
        combined_audio.export(OUTPUT_PATH, format='mp3')

        audio = discord.File(OUTPUT_PATH)
        await interaction.channel.send(file=audio)