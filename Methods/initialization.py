# Standard Library Imports
import ast
import datetime
import re
import inspect
import logging
import atexit
import json
import random
import time
import sqlite3
import os
import io
if os.name == 'nt':
    try:
        import winsound
    except Exception as e:
        print(e)
        pass# Third-Party Library Imports
import peewee
from peewee import Model, CharField, SqliteDatabase
import openai
import elevenlabs
import discord
import easygui
# PROJECT IMPORTS
# Project-Specific Imports
from Methods.system_methods import console_log
from Methods.database_models import *
from Methods.get_key import AcquireKey

# CONSTANTS
USER_INFO_FILE = "MestreSaraData/userinfo.json"
VERSION_INFO_FILE = "versioninfo.json"


def termination():
    console_log(f"Initiation of termination procedures. \n")
    db.close()
    console_log("Termination succeeded.")


class Initialization:
    def __init__(self):
        keys = AcquireKey().get_key()
        self.bot_token = keys["bot_token"]
        self.ai_token = keys["ai_token"]
        self.voice_token = keys["voice_token"]
        # Initialization procedures
        self.intents = None
        self.version_title = None
        self.version = None
        self.version_info = None
        self.activity = None



        try:
            db.connect()
        except peewee.OperationalError as e:
            # If the connection is already open, ignore the exception
            if 'Connection already opened' not in str(e):
                logging.error(e)

        db.create_tables([Whitelist, Censura], safe=True)

    def load_configuration(self):
        LOG_FILE = '../Sara.log'
        TOKEN_FILE = "token.json"

        if os.path.isfile(LOG_FILE) and os.access(LOG_FILE, os.R_OK):
            os.remove('Sara.log')
        logging.basicConfig(filename='Sara.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s', force=True)

        with open(VERSION_INFO_FILE, encoding='utf-8') as version_info_file:
            self.version_info = json.load(version_info_file)

        if os.path.isfile(TOKEN_FILE) and os.access(TOKEN_FILE, os.R_OK):
            console_log("Token detected.")
            openai.api_key = self.ai_token
        else:
            logging.warning("[Initializing...          ] Could not find Token...")
            title = "Insight configuration processus"
            msg = "Insert your service tokens."
            fieldNames = ["Discord", "OpenAI", "ElevenLabs"]
            fieldValues = []  # we start with blanks for the values
            fieldValues = easygui.multenterbox(msg, title, fieldNames)
            token = fieldValues[0]
            openaitoken = fieldValues[1]
            elevenlabs_token = fieldValues[2]

            data = {
                'token': token,
                'openaitoken': openaitoken,
                "elevenlabsapikey": elevenlabs_token,
            }
            with open("token.json", "w") as file:
                json.dump(data, file, indent=4)
                token = open("token.json")
                token = json.load(token)
                token = token["token"]
                return token

    def check_whitelist(self, userid):
        userid = str(userid)
        current_frame = inspect.currentframe()
        top_function = inspect.getframeinfo(current_frame.f_back).function
        try:
            whitelisted = Whitelist.get(Whitelist.userid == userid)
            if whitelisted:
                if "on_message" not in top_function:
                    console_log(f"Whitelisted user command. ID: {userid}")
                return True
        except ValueError:
            return False
        except Exception as err:
            error = str(err)
            if "instance matching query does not exist" in error:
                pass
            else:
                console_log("Erro na verificação da Whitelist:", err)
                logging.error(err)

    def call_intents(self):
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.members = True
        intents = self.intents
        return intents

    def defaultembed(self, title, message):

        self.embed = discord.Embed(title=f"{title}", description=f"{message}", color=0x2ecc71)
        self.embed.set_author(name="Sara Delacroix",
                              icon_url="https://i.pinimg.com/564x/22/76/e8/2276e87294b4ab7a31ac5a60c0c12734.jpg")
        return self.embed