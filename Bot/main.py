# Application Imports
import glob
import time
import typing

import translate
import discord
from discord import app_commands
from discord.ext import tasks, commands
from openai import OpenAI
from nltk.probability import FreqDist
# Databases

# Util Imports
import atexit
import random
from bs4 import BeautifulSoup
import requests
from rich.console import Console
from rich.markdown import Markdown

# Running imports
from dotenv import load_dotenv
from peewee import DoesNotExist

from Bot.Modules.Speech.embeds import whois_embed
from Bot.Modules.Spying.investigate import bing_search, get_from_database, duckduckgo_search
# Modules
from Modules.configuration import *
from Modules.Data.collection import *
from Modules.Data.message_analysis import *
from Modules.Speech.speech import *
# GLOBALS
ENV = "Config/providence.env"


load_dotenv(ENV)
intents = discord.Intents.default()
intents.message_content = True


@atexit.register
def killDatabases():
    logging.info("Killing databases...")
    for db_file in glob.glob("Bot/Data/**/*.db", recursive=True):
        db = SqliteDatabase(db_file)
        if not db.is_closed():
            db.close()
            logging.info(f"Closed database: {db_file}")


if __name__ == '__main__':



    Initialize().makeLogs()
    Initialize().makeTemp()
    Initialize().makeUser()
    logging.info("Logger initialized.")
    client.run(os.getenv('DISCORD_TOKEN'))

