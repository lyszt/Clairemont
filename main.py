import atexit
import requests
import discord
import json
import os
import sqlite3
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib import flow
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


import peewee
from peewee import Model, CharField, SqliteDatabase

# Define the database
db = SqliteDatabase("MestreSaraData/memory.db")

# Constants for file names
# -- GOOGLE API
CLIENT_FILE = 'google.json'
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
# DISCORD
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
        self.bot_token = None
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

        if os.path.isfile(TOKEN_FILE) and os.access(TOKEN_FILE, os.R_OK):
            print("Token detected.")
            with open(TOKEN_FILE, "r") as file:
                token_data = json.load(file)
                self.bot_token = token_data.get("token")
        else:
            CREDENTIALS = None
            if os.path.exists('googletoken.json'):
                credit = Credentials.from_authorized_user_file('googletoken.json', SCOPES)
            if not CREDENTIALS or not CREDENTIALS.valid:
                if CREDENTIALS and CREDENTIALS.expired and CREDENTIALS.refresh_token:
                    CREDENTIALS.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
                    CREDENTIALS = flow.run_local_server(port=0)
                with open('googletoken.json', "w") as token:
                    token.write(CREDENTIALS.to_json())

            try:
                service = build('sheets', 'v4', credentials=CREDENTIALS)
                # CALL THE SHEETS API
                sheet = service.spreadsheets()
                CREDENTIALS_SHEET_ID = '1Joj4DBZ8lvLZXwp-48yuNJkEYQrlxUc5F0c-eENJEi4'
                CREDENTIALS_RANGE = 'B1'

                result = sheet.values().get(spreadsheetId=CREDENTIALS_SHEET_ID,
                                        range=CREDENTIALS_RANGE).execute()
                token = result.get('values',[])
                token = [x[0] for x in token]
                self.bot_token = token[0]
                print(f"Initiating connection with token: {self.bot_token}")
                data = {'token': self.bot_token}
                with open(TOKEN_FILE, "w") as file:
                    json.dump(data, file, indent=4)
                if not token:
                    print("Token has not been found.")
                    return



            except HttpError as e:
                print(e)

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
    bot_token = main_execution.bot_token
    version = main_execution.version_info
    print(f"Mestre Sara {version['version']}: {version['versiontitle']}")
    client.run(bot_token)
