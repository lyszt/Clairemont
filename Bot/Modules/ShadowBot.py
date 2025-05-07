import glob
import logging
import os

import discord
import requests
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
from peewee import SqliteDatabase
from rich.console import Console
from rich.markdown import Markdown

from Bot.Modules.Actions.Actions import Actions
from Bot.Modules.Speech.Speech import Speech


class ShadowBot:
    def __init__(self, intents):
        # GENERAL
        ENV_PATH = ".env"
        load_dotenv(ENV_PATH)
        self.console = Console()
        self.console.log("Initialized console.")

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
            self.last_author_id = message.author.id
            if message.author == self.client.user: return
            if "shadow" in message.content.lower() or "luneta" in message.content.lower() or self.last_author_id == self.client.user.id:
                response = Speech(self.getEnv("GEMINI_TOKEN")).simpleSpeech(message.content)
                self.console.log(response)
                await message.channel.send(response)


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

