import os
import random
import os

import discord


class Shitpost:
    def __init__(self, console):
        self.console = console

    def post(self, message):
        shitpost_collection = [f for f in os.listdir("Resources/Video/") if os.path.isfile(os.path.join("Resources/Video", f))]
        for file in shitpost_collection:
            if message in file:
                return file
        self.console.log("Escolhendo shitpost...")
        return discord.File(f"Resources/Video/{random.choice(shitpost_collection)}")