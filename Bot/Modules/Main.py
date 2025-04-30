import logging
import os

import discord
import requests
from discord import app_commands
from discord.ext import tasks
from rich.console import Console
from rich.markdown import Markdown

from Bot.Modules.Actions.actions import Actions


class Main():

    def __init__(self):
        self.DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)

        self.console = Console(color_system="windows")

        logging.basicConfig(filename='providence.log',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt="%H:%M:%S")
        self.logger = logging.StreamHandler()
        self.logger.setLevel(logging.INFO)
        formatter = formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.logger.setFormatter(formatter)
        logging.getLogger('').addHandler(logging.StreamHandler())


    def run(self):

        action = Actions(self.console, self.logger, self.client)

        self.tree = app_commands.CommandTree(self.client)

        @self.client.event
        async def on_ready():
            await action.changePresence()

            @tasks.loop(minutes=10)
            async def change_presence_task():
                await action.changePresence()

            change_presence_task.start()