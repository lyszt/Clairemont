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
import typing
import asyncio
import collections

from wikipedia import DisambiguationError

from Methods.initialization import Initialization

if os.name == 'nt':
    try:
        import winsound
    except Exception as e:
        print(e)
        pass
# Third-Party Library Imports
import peewee
from peewee import Model, CharField, SqliteDatabase
import openai
import elevenlabs
import discord
import sympy
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext import tasks
import wikipedia
import numpy as np
from requests import get
from sympy import *
import statistics
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from urllib import parse, request

from system_methods import console_log
from database_models import *
import lists


class BotService(discord.client):
    def __init__(self):
        self.DB = SqliteDatabase("MestreSaraData/memory.db")
        self.TEMP = "temp"
        self.censor = Censura.select()
        self.interaction = discord.Interaction



    def run(self, permission_needed, executed_command):
        if permission_needed:
            if self.run_permcheck(self.interaction.user.id):
                exec(f"Command().{executed_command}()")
            else:
                console_log("Usuário tentou utilizar comandos sem permissão.")
                self.interaction.channel.send("Desculpe, você não tem permissão para usar este comando.")
    def run_permcheck(self, author):
        target = int(author)
        whitelisted = Initialization().check_whitelist(self.interaction.user.id)
        return whitelisted

    # COMMANDS

    class Commands():
        def __init__(self):
            self.DB = SqliteDatabase("MestreSaraData/memory.db")
            self.TEMP = "temp"
            self.censura = Censura.select()
            self.default_embed = Initialization().defaultembed
        def gift_command(self, interaction: discord.Interaction, message, target):
            embedVar = self.default_embed(
                f"{interaction.user.display_name} acabou de presentar {target.display_name}! O que será o presente misterioso? 😨",
                f"Tem uma nota escrito **'{message}'**")
            embedVar.set_thumbnail(url=target.avatar)
            interaction.response.send_message(embed=embedVar)
            url = "http://api.giphy.com/v1/gifs/search"
            params = parse.urlencode({
                "q": "lootbox",
                "api_key": "8AkWlssazxQ5ohXq3MlOBo2FLPkFDexa",
                "limit": "11"
            })

            with request.urlopen("".join((url, "?", params))) as response:
                data = json.loads(response.read())
                try:
                    gif_choice = random.randint(1, 10)
                    gif_url = data['data'][gif_choice]['images']['fixed_height']['url']
                except IndexError:
                    gif_url = data['data'][0]['images']['fixed_height']['url']
            interaction.channel.send(f"{gif_url}")
            wikipedia.set_lang("pt")
            while True:
                try:
                    item = wikipedia.random(1)
                    presente = wikipedia.summary(item)
                    break
                except wikipedia.DisambiguationError:
                    item = wikipedia.random(1)
                    presente = wikipedia.summary(item)
                    continue
            try:
                images = wikipedia.page(item).images
                result_image = [image for image in images if
                                str.lower(image).__contains__(f"{presente.split(' ')[0]}") and '.svg' not in image][0]
            except IndexError:
                params = parse.urlencode({
                    "q": f"{presente.split(' ')[0]}",
                    "api_key": "8AkWlssazxQ5ohXq3MlOBo2FLPkFDexa",
                    "limit": "11"
                })
                url = "http://api.giphy.com/v1/gifs/search"
                with request.urlopen("".join((url, "?", params))) as response:
                    data = json.loads(response.read())
                    try:
                        gif_choice = random.randint(1, 10)
                        result_image = data['data'][gif_choice]['images']['fixed_height']['url']
                    except IndexError:
                        result_image = data['data'][0]['images']['fixed_height']['url']
                        if not result_image:
                            result_image = "https://static.wikia.nocookie.net/sd-reborn/images/3/31/Obama.png/revision/latest/thumbnail/width/360/height/360?cb=20221021132625"

            sumario = presente[:256]
            embedVar = self.default_embed(f"Uau, {target.display_name}! É um {item} 🤯! Que presentasso!", f"{sumario}(...)")
            embedVar.add_field(name="", value=f"<@{target.id}>! E aí, gostou?")
            embedVar.set_image(url=result_image)
            interaction.channel.send(embed=embedVar)
