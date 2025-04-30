from datetime import datetime

import discord
import logging


class Actions():

    def __init__(self, logger, console, client):
        self.logger = logger
        self.console = console
        self.client = client

    async def changePresence(self):
        logging.info(f"Providence initialized at {datetime.now()}")
        logging.info("Backing up previous databases.")
        await self.client.wait_until_ready()
        await self.tree.sync(guild=None)
        logging.info("Synced.")

        async def create_presence():
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
