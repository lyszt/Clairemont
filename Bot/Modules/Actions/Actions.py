from datetime import datetime

import discord
import logging
from Bot.Modules.Actions.QuoteFetcher import QuoteFetcher


class Actions:

    def __init__(self, tree, console, client):
        self.console = console
        self.client = client
        self.tree = tree


    def getConsole(self):
        return self.console
    def getClient(self):
        return self.client
    def getTree(self):
        return self.tree

    async def change_presence(self):
        self.console.log(f"Providence initialized at {datetime.now()}")
        self.console.log("Backing up previous databases.")
        await self.client.wait_until_ready()
        await self.tree.sync(guild=None)
        self.console.log("Synced.")

        presence_status = QuoteFetcher(self.console).fetch_random_quote().get_quote()
        if presence_status == "" or "QUERY LIMITED EXCEEDED" in presence_status or presence_status is None:
            presence_status = "Shadow da sombra te assombra."
        try:
            await self.client.change_presence(
                status=discord.Status.dnd,
                activity=discord.Activity(
                    type=discord.ActivityType.streaming,
                    name=f": {presence_status}",
                    url="https://youtu.be/rSpUx2LrPOw"
                )
            )
        except Exception as e:
            logging.info("Could not change presence: ", e)

