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

from Bot.Modules.ShadowBot import ShadowBot

# GLOBALS
intents = discord.Intents.default()
intents.message_content = True


if __name__ == '__main__':
    Shadow = ShadowBot()
    Shadow.run()


    @atexit.register
    def killDatabases():
        Shadow.killDatabases()