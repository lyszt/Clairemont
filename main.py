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

async def lackPermissions(interaction: discord.Interaction):
    console_log("Usuário tentou utilizar comandos sem permissão.")
    await interaction.response.send_message("Desculpe, você não tem permissão para usar este comando.")


@tree.command(name="presentear", description="Dê um presente de natal para um amigo!")
async def self(interaction: discord.Interaction, mensagem: str, alvo: discord.User):
        if alvo:
            default_embed = Initialization().defaultembed
            embedVar = default_embed(f"{interaction.user.display_name} acabou de presentar {alvo.display_name}! O que será o presente misterioso? 😨",f"Tem uma nota escrito **'{mensagem}'**")
            embedVar.set_thumbnail(url=alvo.avatar)
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
                result_image = [image for image in images if str.lower(image).__contains__(f"{presente.split(' ')[0]}") and '.svg' not in image][0]
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
            embedVar = default_embed(f"Uau, {alvo.display_name}! É um {item} 🤯! Que presentasso!", f"{sumario}(...)")
            embedVar.add_field(name="", value=f"<@{alvo.id}>! E aí, gostou?")
            embedVar.set_image(url=result_image)
            await interaction.channel.send(embed=embedVar)



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


@tree.command(name="censurar", description="Censurar palavras para uso do bot.")
async def self(interaction: discord.Interaction, palavra: str):
    palavra = palavra.lower()
    palavras_censuradas = [word.strip() for word in palavra.split(",")]

    whitelisted = Initialization().check_whitelist(interaction.user.id)
    default_embed = Initialization().defaultembed

    if whitelisted:
        try:
            with db.atomic():
                # Insert the censored words into the Censura table
                for word in palavras_censuradas:
                    Censura.create(palavra=word)

            console_log(f"{len(palavras_censuradas)} palavras censuradas.")
            await interaction.response.send_message("Censurando...")
            await interaction.edit_original_response(
                embed=default_embed("Censurado com sucesso.", f"{len(palavras_censuradas)} palavras censuradas."))
        except Exception as e:
            console_log("Erro detectado:", e)

@tree.command(name="interpretarnpc",
              description="Interprete um personagem.")
async def self(interaction: discord.Interaction, nomenpc: str, titulo: typing.Optional[str],
               image: typing.Optional[str], dialogo: str, ):
    embed = discord.Embed(title=f"", color=15277667, description=f"{dialogo}",
                          timestamp=datetime.datetime.now())
    imagem = (f"{image}" if image else "https://i.pinimg.com/564x/ef/d9/46/efd946986bfc8ab131353d84fd6ce538.jpg")
    if titulo:
        embed.set_author(name=f"{nomenpc}, {titulo} diz:", icon_url=imagem)
    else:
        embed.set_author(name=f"{nomenpc} diz:", icon_url=imagem)
    await interaction.response.send_message(embed=embed)


@tree.command(name="citacao",
              description="Citação da última mensagem enviada.")
async def self(interaction: discord.Interaction):
    message = [message async for message in interaction.channel.history(limit=3)]
    dialogo = message[0].content
    usuario = message[0].author.id
    usuarionome = message[0].author.name
    imagem = message[0].author.avatar
    embed = discord.Embed(title=f'''"{dialogo}"''', color=10070709, description=f"")
    embed.set_image(url=imagem)
    embed.add_field(name="", value=f"<@{usuario}>, {datetime.datetime.today().year}")
    await interaction.response.send_message(embed=embed)


@tree.command(name="meme",
              description="Meme.")
async def self(interaction: discord.Interaction):
    meme = get("https://meme-api.com/gimme").text
    data = json.loads(meme, )
    embed = discord.Embed(title=f"{data['title']}", color=discord.Color.random()).set_image(
        url=f"{data['url']}")
    await interaction.response.send_message(embed=embed)

@tree.command(name="talk", description="Converse com a Sara.")
async def self(interaction: discord.Interaction, dialogue: str, voice: typing.Optional[bool] = False):
    async def sendMessage(message):
        embed = discord.Embed(title=f"{dialogue if len(dialogue) < 256 else 'Questão analisada...'}",
                              color=15277667,
                              description=f"Sara responde: \n\n {message}",
                              )
        embed.set_image(url="https://i.pinimg.com/564x/9a/a3/0f/9aa30f656fab84d1e03e87b8f5d25451.jpg")
        await interaction.edit_original_response(embed=embed)

    whitelisted = Initialization().check_whitelist(interaction.user.id)
    if whitelisted:
        await interaction.response.send_message("Gerando...")
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Você é Sara, uma taverneira do Caiçara. Você é uma pessoa animada, boa, sensível e tem muitos hobbies. Você ama pessoas. Responda com naturalidade."},
                {"role": "user", "content": dialogue}
            ]

        )
        await sendMessage(completion.choices[0].message.content)
        if voice:
            audio = elevenlabs.generate(
                text=completion.choices[0].message.content,
                voice="Freya",
                model="eleven_multilingual_v1"
            )
            elevenlabs.save(audio, "temp/speech.mp3")
            await interaction.channel.send(file=discord.File("temp/speech.mp3"))



    else:
        await lackPermissions(interaction)


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
