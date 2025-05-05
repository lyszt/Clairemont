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

from Bot.Modules.Actions.actions import Actions


class Main:
    console = Console(color_system="windows")

    def __init__(self):
        self.console.log("Initialized console.")
        self.DISCORD_TOKEN = self.getEnv("DISCORD_TOKEN")
        if self.DISCORD_TOKEN == "":
            self.console.log("Could not find DISCORD_TOKEN, exiting.")
            exit(1)
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        self.tree = app_commands.CommandTree(self.client)

        action = Actions(self.tree, self.console, self.client)

        @self.client.event
        async def on_ready():
            self.console.log("DISCORD CLIENT - [ Ready ].")
            await action.changePresence()

            @tasks.loop(minutes=10)
            async def change_presence_task():
                await action.changePresence()
                change_presence_task.start()

    def run(self):
        self.client.run(self.DISCORD_TOKEN)

    def getEnv(self, variable: str) -> str:
        try:
            self.console.log(f"Getting environment variable: {variable}")
            ENV_PATH = ".env"
            load_dotenv(ENV_PATH)
            if os.getenv(variable) is None:
                self.console.log("Environment variable not set.")
                return ""
            env_var = os.environ.get(variable)
            self.console.log(f"Acquired environment variable: {env_var[:5]}...")
            return env_var
        except Exception as err:
            raise Exception(f"Environment variable {variable} not found. - {err.args} : {err}")

    def killDatabases(self):
        self.console.log(f"Killing databases...")
        for db_file in glob.glob("Bot/Data/**/*.db", recursive=True):
            db = SqliteDatabase(db_file)
            if not db.is_closed():
                db.close()
                logging.info(f"Closed database: {db_file}")

