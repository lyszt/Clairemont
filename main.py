import ast
import datetime
import typing

from requests import get

from comandos import *
import discord
import sympy
from discord.app_commands import Choice
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Bot
import json
import random, time
import wikipedia
import sqlite3
import os, io
import numpy as np
from sympy import *
import statistics
import typing

conn = sqlite3.connect("MilitaryData/memory.db")
cur = conn.cursor()


class MainExecution:

    def __init__(self):

        self.intents = None
        self.version_title = None
        self.version = None
        self.version_info = None
        self.activity = None
        self.setversioninfo()
        self.setuserinfo()
        self.initializedatabase()

    def checkwhitelist(self, userid):

        whitelist = cur.execute('''SELECT userid FROM whitelist;

        ''').fetchone()

        userid = str(userid)
        print(whitelist)
        id_check = any(user in userid for user in whitelist)
        if id_check:
            print("Whitelisted user used a command.")
        return id_check

    def initializedatabase(self):
        cur.execute('''
                            CREATE TABLE IF NOT EXISTS frases(entrada TXT, saida1 TXT, saida2 TXT, saida3 TXT);
                ''')
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS whitelist(userid INT);
        ''')
        cur.execute('''
                            CREATE TABLE IF NOT EXISTS rps(titulo TEXT, descricao TEXT, autor TEXT, imagem TEXT);
                ''')

        cur.execute('''
                                    CREATE TABLE IF NOT EXISTS fichaRP(titulorp TEXT, jogador TEXT, nomepersonagem TEXT, personalidade TEXT, idade TEXT, habilidades TEXT, aparencia TEXT, historia TEXT, imagem TEXT, genero TEXT);
                        ''')
        cur.execute('''
                                            CREATE TABLE IF NOT EXISTS censura(palavra TEXT);
                                ''')

    def tokenload(self):
        if os.path.isfile("token.json") and os.access("token.json", os.R_OK):
            print("Token detected.")
            token = open("token.json")
            token = json.load(token)
            token = token["token"]
            return token
        else:
            token = input("Inform the token to activate Providentia. \n")
            data = {
                'token': token
            }
            with open("token.json", "w") as file:
                json.dump(data, file, indent=4)
            token = open("token.json")
            token = json.load(token)
            token = token["token"]
            return token

    def setuserinfo(self):
        user_info = open("MilitaryData/userinfo.json")
        user_info = json.load(user_info)
        return user_info

    def callIntents(self):
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        intents = self.intents
        return intents

    def setversioninfo(self):
        version_info = open('versioninfo.json', encoding='utf-8')
        self.version_info = json.load(version_info)
        self.version = self.version_info["version"]
        self.version_title = self.version_info["versiontitle"]

        return self.version_info

    def defaultembed(self, title, message):

        self.embed_configuration = discord.Embed(title=f"{title}", description=f"{message}", color=0x2ecc71)
        self.embed_configuration.set_author(name="PLYG-7X42",
                                            icon_url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/9f1ed69b-9e98-4f78-acda-c95c6f4be159/db73tp3-8c5589a6-051c-4408-b244-f451c599b04d.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzlmMWVkNjliLTllOTgtNGY3OC1hY2RhLWM5NWM2ZjRiZTE1OVwvZGI3M3RwMy04YzU1ODlhNi0wNTFjLTQ0MDgtYjI0NC1mNDUxYzU5OWIwNGQuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.7X4JjtqAwnetH9HC9f4sl3kcik8VCFCE5nr1MGB607M")
        return self.embed_configuration

class aclient(discord.Client):

    def __init__(self):
        intents = MainExecution().callIntents()
        super().__init__(intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
        await self.change_presence(status=discord.Status.dnd, activity=(
            discord.Activity(type=discord.ActivityType.listening, name="aos meios de comunicações inimigos.")))

    async def on_message(self, message):
        pass


# EVENTS

client = aclient()
tree = app_commands.CommandTree(client)
version_info = MainExecution().setversioninfo()
user_info = MainExecution().setuserinfo()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(
        "The key words of economics are urbanization, industrialization, centralization, efficiency, quantity, speed.")
    MainExecution()
    token = MainExecution().tokenload()
    version = MainExecution().setversioninfo()
    print(f"Providentia {version['version']}: {version['versiontitle']}")
    client.run(token)

conn.close()
cur.close()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
