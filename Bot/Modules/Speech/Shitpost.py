import os
import random
import os

import discord


class Shitpost:
    def __init__(self, console):
        self.console = console

    def post(self, message):
        shitpost_collection = [f for f in os.listdir("Resources/Video/Shitpost/") if os.path.isfile(os.path.join("Resources/Video/Shitpost/", f))]
        for file in shitpost_collection:
            if message in file:
                return file
        self.console.log("Escolhendo shitpost...")
        return discord.File(f"Resources/Video/Shitpost/{random.choice(shitpost_collection)}")
    def self_post(self, message):
        self_photos = [f for f in os.listdir("Resources/Video/Sara/") if
                               os.path.isfile(os.path.join("Resources/Video/Sara/", f))]
        for file in self_photos:
            if message in file:
                return file
        self.console.log("Escolhendo shitpost...")
        return discord.File(f"Resources/Video/Sara/{random.choice(self_photos)}")