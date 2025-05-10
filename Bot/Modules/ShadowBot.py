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
            past_messages = [msg async for msg in message.channel.history(limit=5)]
            conversational_context = "\n".join(
                f"{msg.author.name} diz: {msg.content}" for msg in past_messages
            )
            if message.author == self.client.user: return
            if ("shadow" in message.content.lower() or "luneta" in message.content.lower()) or (past_messages[1].author.id == self.client.user.id and random.randint(1,2) == 1):
                response = Speech(self.getEnv("GEMINI_TOKEN")).contextSpeech(message.content, conversational_context)
                self.console.log(response)
                await message.channel.send(response)

        @self.tree.command(name="collect")
        async def collect(interaction: discord.Interaction):
            await dataCommands(self.console, self.client).collect(interaction)

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

