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
# Third-Party Library Imports
import google.generativeai as genai
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
from wikipedia import DisambiguationError
import numpy as np
from requests import get
from sympy import *
import statistics
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from urllib import parse, request

if os.name == 'nt':
    try:
        import winsound
    except Exception as e:
        print(e)
        pass

from Methods.initialization import Initialization
from Methods.initialization import *
from Methods.system_methods import console_log
from Methods.database_models import *
from Methods.command_parser import *
from Methods.languagemodel import GenerateText
import lists


class BotService:
    arguments = None

    def __init__(self):
        self.DB = SqliteDatabase("MestreSaraData/memory.db")
        self.TEMP = "temp"
        self.censor = Censura.select()
        self.interaction = None

    async def run(self, interaction, permission_needed, command_code, arguments):
        # Defines global interaction for general use in permchecks
        self.interaction = interaction

        try:
            BotService.arguments = [argument for argument in arguments]
            if permission_needed:
                if await self.run_permcheck(interaction.user.id):
                    await execute_by_code(interaction, self, command_code)
                else:
                    logging.info("Usuário tentou utilizar comandos sem permissão.")
                    self.interaction.channel.send("Desculpe, você não tem permissão para usar este comando.")
            else:
                await execute_by_code(interaction, self, command_code)
        except Exception as err:
                logging.error(f"[ERROR IN COMMAND    ]", err)
                print(err)
    async def run_permcheck(self, author):
        target = int(author)
        whitelisted = Initialization().check_whitelist(self.interaction.user.id)
        return whitelisted

    # COMMANDS

    class Commands:
        def __init__(self):
            self.DB = SqliteDatabase("MestreSaraData/memory.db")
            self.TEMP = "temp"
            self.censura = Censura.select()
            self.default_embed = Initialization().defaultembed

        async def gift_command(self, interaction):
            message = BotService.arguments[0]
            target = BotService.arguments[1]

            embedVar = self.default_embed(
                f"{interaction.user.display_name} acabou de presentar {target.display_name}! O que será o presente misterioso? 😨",
                f"Tem uma nota escrito **'{message}'**")
            embedVar.set_thumbnail(url=target.avatar)
            await interaction.response.send_message(embed=embedVar)
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
            await interaction.channel.send(f"{gif_url}")
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
            embedVar = self.default_embed(f"Uau, {target.display_name}! É um {item} 🤯! Que presentasso!",
                                          f"{sumario}(...)")
            embedVar.add_field(name="", value=f"<@{target.id}>! E aí, gostou?")
            embedVar.set_image(url=result_image)
            await interaction.channel.send(embed=embedVar)

        async def talk_command(self, interaction):
            dialogue = BotService.arguments[0]
            voice = BotService.arguments[1]
            async def sendMessage(message):
                embed = discord.Embed(title=f"{dialogue if len(dialogue) < 256 else 'Questão analisada...'}",
                                      color=15277667,
                                      description=f"Sara responde: \n\n {message}",
                                      )

                image_file = discord.File("../temp/stablediffusion.jpg", filename="image.jpg")
                embed.set_image(url="attachment://image.jpg")
                await interaction.edit_original_response(file=image_file, embed=embed)

            embed = self.default_embed("Pensando...","Espera só um minuto :)")
            await interaction.response.send_message(embed=embed)
            logging.info("[GENERATING GPT 3.5 TEXT    ]")
            response = GenerateText().run(dialogue)
            await sendMessage(response)
            if voice:
                audio = elevenlabs.generate(
                    text=response,
                    voice="Freya",
                    model="eleven_multilingual_v1"
                )
                elevenlabs.save(audio, "temp/speech.mp3")
                await interaction.channel.send(file=discord.File("temp/speech.mp3"))