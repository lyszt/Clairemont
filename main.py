import atexit

import discord
import json
import os
import sqlite3

import peewee
from peewee import Model, CharField, SqliteDatabase

# Define the database
db = SqliteDatabase("MestreSaraData/memory.db")

# Constants for file names
TOKEN_FILE = "token.json"
USER_INFO_FILE = "MestreSaraData/userinfo.json"
VERSION_INFO_FILE = "versioninfo.json"

# Define a Peewee model for the whitelist
class Whitelist(Model):
    userid = CharField(unique=True)

    class Meta:
        database = db

class MainExecution:
    def __init__(self):
        self.version_info = None
        self.token = None
        self.initialize_database()
        self.load_configuration()

    def check_whitelist(self, userid):
        try:
            Whitelist.get(Whitelist.userid == userid)
            print("Whitelisted user used a command.")
            return True
        except Whitelist.DoesNotExist:
            return False

    def initialize_database(self):
        try:
            db.connect()
        except peewee.OperationalError as e:
            # If the connection is already open, ignore the exception
            if 'Connection already opened' not in str(e):
                raise  # If it's a different OperationalError, raise it

        db.create_tables([Whitelist], safe=True)

    def load_configuration(self):
        # Load version information
        with open(VERSION_INFO_FILE, encoding='utf-8') as version_info_file:
            self.version_info = json.load(version_info_file)

        # Load token
        if os.path.isfile(TOKEN_FILE) and os.access(TOKEN_FILE, os.R_OK):
            print("Token detected.")
            with open(TOKEN_FILE, "r") as file:
                token_data = json.load(file)
                self.token = token_data.get("token")
        else:
            self.token = input("Enter the token to activate Mestre Sara: \n")
            data = {'token': self.token}
            with open(TOKEN_FILE, "w") as file:
                json.dump(data, file, indent=4)

    def call_intents(self):
        intents = discord.Intents.default()
        intents.message_content = True
        return intents

    def default_embed(self, title, message):
        embed = discord.Embed(
            title=f"{title}",
            description=f"{message}",
            color=0x2ecc71
        )
        embed.set_author(
            name="PLYG-7X42",
            icon_url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/9f1ed69b-9e98-4f78-acda-c95c6f4be159/db73tp3-8c5589a6-051c-4408-b244-f451c599b04d.jpg?token=YOUR_TOKEN_HERE"
        )
        return embed

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=MainExecution().call_intents())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await self.sync_data()
        await self.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="os clientes tagarelar na Taverna da Sara."
            )
        )

    async def on_message(self, message):
        pass

    async def sync_data(self):
        # Implement advanced data synchronization logic here
        pass

    # Close the database connection
    atexit.register(db.close)

if __name__ == '__main__':
    print("The keywords of the economy are urbanization, industrialization, centralization, efficiency, quantity, velocity.")
    main_execution = MainExecution()
    client = aclient()
    token = main_execution.token
    version = main_execution.version_info
    print(f"Mestre Sara {version['version']}: {version['versiontitle']}")
    client.run(token)
