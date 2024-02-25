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
import typing
import asyncio
import collections

from wikipedia import DisambiguationError

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

# Project-Specific Imports
from comandos import *
from Methods.system_methods import console_log
from Methods.initialization import Initialization, termination
from Methods.database_models import *
from Methods.commands import *
import lists

# Logging
LOG_FILE = 'Sara.log'
if os.path.isfile(LOG_FILE) and os.access(LOG_FILE, os.R_OK):
    os.remove('Sara.log')
logging.basicConfig(filename='Sara.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# CONSTANTS
DB = SqliteDatabase("MestreSaraData/memory.db")
TEMP = "temp"

if os.path.exists(TEMP) and os.path.isdir(TEMP):
    for filename in os.listdir(TEMP):
        file_path = os.path.join(TEMP, filename)
        os.remove(file_path)
else:
    os.mkdir(TEMP)

censura = Censura.select()


class aclient(discord.Client):

    def __init__(self):
        intents = Initialization().call_intents()
        super().__init__(intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
        await self.change_presence(status=discord.Status.dnd, activity=(
            discord.Activity(type=discord.ActivityType.listening, name=random.choice(lists.variacoes))))

    @tasks.loop(minutes=10)
    async def change_presence_task(self):
        try:
            await client.change_presence(
                status=discord.Status.dnd,
                activity=discord.Activity(
                    type=discord.ActivityType.listening,
                    name=random.choice(lists.variacoes)
                )
            )
        except Exception as e:
            console_log("Erro na mudança de presença", e)
        self.change_presence_task.start()

    async def on_message(self, message):
        pass


# EVENTS

client = aclient()
tree = app_commands.CommandTree(client)


@tree.command(name="presentear", description="Dê um presente de natal para um amigo!")
async def self(interaction: discord.Interaction, mensagem: str, alvo: discord.User):
    await BotService().run(interaction,False, "gift_command", [mensagem, alvo])


@tree.command(name="whitelist",
              description="Adicionar usuário a lista de operações da Sara.",
              )
async def self(interaction: discord.Interaction, userid: str, add_remove: str):
    id = int(userid)
    whitelisted = Initialization().check_whitelist(interaction.user.id)
    default_embed = Initialization().defaultembed
    if whitelisted:
        try:
            if add_remove == 'add':
                try:
                    Whitelist.get(Whitelist.userid == userid)
                    embed = default_embed(f"Não pude usar este comando.",
                                          f"Usuário já está na Whitelist.")
                    await interaction.response.send_message(embed=embed)
                except Whitelist.DoesNotExist:
                    user_entry = Whitelist.create(userid=userid)
                    user_entry.save()
                    console_log(f"Usuário {userid} adicionado na Whitelist.")
                    embed = default_embed(f"Sucesso.", f"<@{userid}> adicionado na Whitelist.")
                    await interaction.response.send_message(embed=embed)

                except ValueError:
                    embed = default_embed(f"Valor inválido.", f"Insira um id inteiro.")
                    await interaction.response.send_message(embed=embed)
                except Exception as e:
                    console_log("Erro na adição na Whitelist:", e)

            elif add_remove == 'remove':
                userid = int(id)
                try:
                    condition = (Whitelist.get(Whitelist.userid == userid))
                    remove_from_whitelist = Whitelist.delete().where(condition).execute()
                    console_log(f"Usuário {userid} removido da Whitelist.")
                    embed = default_embed(f"Sucesso.",
                                          f"{remove_from_whitelist} usuário removido da Whitelist. ID: {userid}")
                    await interaction.response.send_message(embed=embed)
                except ValueError:
                    embed = default_embed(f"Valor inválido.", f"Insira um id inteiro.")
                    await interaction.response.send_message(embed=embed)
                except Exception as e:
                    console_log("Erro na remoção da Whitelist:", e)
            else:
                pass
        except ValueError:
            embedVar = default_embed(f"Valor inválido.", f"Insira um id inteiro.")
            await interaction.response.send_message(embed=embedVar)
        except Exception as e:
            console_log("Erro na remoção da Whitelist:", e)
    else:
        await lackPermissions(interaction)

@tree.command(name="talk", description="Converse com a Sara.")
async def self(interaction: discord.Interaction, dialogue: str, voice: typing.Optional[bool] = False, image_generation: typing.Optional[bool] = False):
    await BotService().run(interaction,True, "talk_command", [dialogue, voice, image_generation])

if __name__ == '__main__':
    console_log(
        "The key words of economics are urbanization, industrialization, centralization, efficiency, quantity, speed.")
    console_log("Initializing...")
    try:
        bot_init = Initialization()
        bot_init.load_configuration()
        bot_token = bot_init.bot_token
        version = bot_init.version_info
        console_log(f"Sara {version.get('version')}: {version.get('versiontitle')}")
        console_log("Pre-requisites of initialization completed.")
    except Exception as err:
        console_log("Error while managing pre-requisites of inicialization.", err)
        logging.error(err)
        raise
    try:
        client.run(bot_token)
    except Exception as err:
        console_log("Error while executing the client.", err)
        logging.error(err)
        raise
    atexit.register(termination)
