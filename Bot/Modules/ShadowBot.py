import glob
import logging
import os
import random

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
from peewee import SqliteDatabase
from rich.console import Console

from Bot.Modules.Actions.Actions import Actions
from Bot.Modules.Data.InitializeDatabases import InitializeDatabases
from Bot.Modules.Data.dataCommands import dataCommands
from Bot.Modules.Math.graphing import Graphing
from Bot.Modules.Speech.AudioGen import AudioGen
from Bot.Modules.Speech.Embed import Embed
from Bot.Modules.Speech.RandomInteraction import RandomInteraction
from Bot.Modules.Speech.Shitpost import Shitpost
from Bot.Modules.Speech.Speech import Speech


class ShadowBot:
    def __init__(self, intents, directory):
        # GENERAL
        self.directory = directory
        ENV_PATH = ".env"
        load_dotenv(ENV_PATH)
        self.console = Console()
        self.console.log("Initialized console.")
        self.initializeDatabases()
        # This needs to be improved. A database would suffice.
        self.allowed_users = [779546493425287180, 1047943536374464583, 226518042895581184]
        # DISCORD
        self.DISCORD_TOKEN = self.getEnv("DISCORD_TOKEN")
        if self.DISCORD_TOKEN == "":
            self.console.log("Could not find DISCORD_TOKEN, exiting.")
            exit(1)

        self.client = discord.Client(intents=intents)
        self.tree = app_commands.CommandTree(self.client)

        # ACTIONS ABSTRACTS COMMANDS
        action = Actions(self.tree, self.console, self.client)


        @self.client.event
        async def on_ready():
            self.console.log("DISCORD CLIENT - [ Ready ].")
            await change_presence_task.start()


        @tasks.loop(minutes=10)
        async def change_presence_task():
            await action.change_presence()

        self.last_author_id = None

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return

            allowed_guilds = [452243234002042880, 696830110493573190]
            allowed_channels = [704066892972949507]

            should_reply = (
                    "sara" in message.content.lower() or
                    f"<@{self.client.user.id}>" in message.content
            )


            is_allowed_location = message.guild.id in allowed_guilds or message.channel.id in allowed_channels
            if should_reply and is_allowed_location:

                    async with message.channel.typing():

                        past_messages = [msg async for msg in message.channel.history(limit=5)]
                        conversational_context = "\n".join(
                            f"{msg.author.name} says: {msg.content}" for msg in reversed(past_messages)
                        )

                        self.console.log(f"✨ Sara is thinking about a response to '{message.content}'... ✨")
                        response_text = Speech(self.getEnv("GEMINI_TOKEN"), self.console).contextSpeech(message.content,
                                                                                                        conversational_context)
                        self.console.log(f"Sara's thought: {response_text}")

                        sara_embed = Embed.create(
                            title="From behind the counter, Sara replies...",
                            description=response_text,
                            footer_text="Taverna do Caiçara •",
                        )
                        await message.channel.send(embed=sara_embed)
                        await RandomInteraction(self.console, self.getEnv("OPENAI_API_KEY")).choose_interaction(message, response_text, conversational_context)

        @self.tree.command(name="collect")
        async def collect(interaction: discord.Interaction):
            if interaction.user.id in self.allowed_users:
                await dataCommands(self.console, self.client).collect(interaction)

        @self.tree.command(name="collect_to_text")
        async def collect(interaction: discord.Interaction):
            if interaction.user.id in self.allowed_users:
                await dataCommands(self.console, self.client).collect_to_text(interaction)
        @self.tree.command(name="fx")
        async def f_of_x(interaction: discord.Interaction, function: str):
            await interaction.response.defer()
            try:
                Graphing(self.console).graph_2d(function)
                await interaction.followup.send(file=discord.File("graph_2d.jpg"))
            except Exception as e:
                self.console.log(e)
                await interaction.followup.send("Não consegui colocar essa função em um gráfico.", ephemeral=True)

        @self.tree.command(name="fxy")
        async def f_of_x_y(interaction: discord.Interaction, function: str):
            await interaction.response.defer()
            function = function.replace("²", "**2")
            try:
                Graphing(self.console).graph_3d(function)
                await interaction.followup.send(file=discord.File("graph_3d.jpg"))
            except Exception as e:
                self.console.log(e)
                await interaction.followup.send("Não consegui colocar essa função em um gráfico. Dá uma olhada pra ver o que arrumar.")

    def getClient(self):
        return self.client
    def getTree(self):
        return self.tree

    def run(self):
        self.client.run(self.DISCORD_TOKEN)

    def getEnv(self, variable: str) -> str:
        try:
            self.console.log(f"Getting environment variable: {variable}")

            if os.getenv(variable) is None:
                self.console.log("Environment variable not set.")
                return ""
            env_var = os.environ.get(variable)
            self.console.log(f"Acquired environment variable: {env_var[:5]}...")
            return env_var
        except Exception as err:
            raise Exception(f"Environment variable {variable} not found. - {err.args} : {err}")

    def initializeDatabases(self):
        self.console.log("Initializing databases.")
        InitializeDatabases(self.console, self.directory).initializeCorte()
    def killDatabases(self):
        self.console.log("Killing databases...")
        for db_file in glob.glob("Bot/Data/**/*.db", recursive=True):
            try:
                db = SqliteDatabase(db_file)
                if not db.is_closed():
                    db.close()
                logging.info(f"Closed database: {db_file}")
            except Exception as e:
                self.console.log(f"Failed to close database {db_file}: {e}")

