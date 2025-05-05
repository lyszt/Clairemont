from datetime import datetime

import discord
import logging

import requests

from Bot.Modules.Actions.MakeRequests import QuoteFetcher


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
        if presence_status == "":
            presence_status = "Take your time."
        try:
            await self.client.change_presence(
                status=discord.Status.dnd,
                activity=discord.Activity(
                    type=discord.ActivityType.streaming,
                    name=f": {presence_status}",
                    url="https://www.youtube.com/watch?v=wATOtesXrqw"
                )
            )
        except Exception as e:
            logging.info("Could not change presence: ", e)

