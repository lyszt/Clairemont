import glob
import logging
import os
import random

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
from peewee import SqliteDatabase
from rich.console import Console

from Bot.Modules.Actions.Actions import Actions
from Bot.Modules.Actions.Sigaa import Sigaa
from Bot.Modules.Data.InitializeDatabases import InitializeDatabases
from Bot.Modules.Data.dataCommands import dataCommands
from Bot.Modules.Math.graphing import Graphing
from Bot.Modules.Math.math import Math
from Bot.Modules.Speech.AudioGen import AudioGen
from Bot.Modules.Speech.Embed import Embed
from Bot.Modules.Speech.RandomInteraction import RandomInteraction
from Bot.Modules.Speech.Shitpost import Shitpost
from Bot.Modules.Speech.Speech import Speech
from Bot.Modules.Speech.Thinking import Thinking
from Bot.Modules.Actions.WebDriver import WebDriver

class ShadowBot:
    def __init__(self, intents, directory):
        self.directory = directory
        ENV_PATH = ".env"
        load_dotenv(ENV_PATH)
        self.console = Console()
        self.console.log("Console initialisée.")
        self.initializeDatabases()
        self.allowed_users = [779546493425287180, 1047943536374464583, 226518042895581184]

        # DISCORD
        self.DISCORD_TOKEN = self.getEnv("DISCORD_TOKEN")
        if self.DISCORD_TOKEN == "":
            self.console.log("Impossible de trouver le DISCORD_TOKEN, arrêt du programme.")
            exit(1)

        self.client = discord.Client(intents=intents)
        self.tree = app_commands.CommandTree(self.client)
        self.decision_maker = Thinking(self.getEnv("GEMINI_TOKEN"), console=self.console)

        action = Actions(self.tree, self.console, self.client)
        self.commands = {
            "simplify": self._simplify,
            "fx": self._graph_2d,
            "fxy": self._graph_3d,
            "get_college_information": self._get_college_information,
            "expand_polynomial": self._expand_polynomial
        }

        @self.client.event
        async def on_ready():
            self.console.log("CLIENT DISCORD - [ Prêt ].")
            await change_presence_task.start()

        @tasks.loop(minutes=10)
        async def change_presence_task():
            await action.change_presence()

        self.last_author_id = None

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return

            allowed_guilds = [452243234002042880, 696830110493573190]
            allowed_channels = [704066892972949507]

            should_reply = (
                "sara" in message.content.lower() or
                f"<@{self.client.user.id}>" in message.content
            )

            is_allowed_location = message.guild.id in allowed_guilds or message.channel.id in allowed_channels
            if should_reply and is_allowed_location:
                async with message.channel.typing():
                    command_data = self.decision_maker.get_bot_command(message.content)
                    command_name = command_data.get("command")
                    api_key = self.getEnv("GEMINI_TOKEN")

                    if command_name in self.commands:
                        command_arg = command_data.get("arg")
                        command_to_execute = self.commands[command_name]
                        argless_commands = ["get_college_information"]
                        if command_name in argless_commands:
                            command_information = await command_to_execute()
                        else:
                            command_information = await command_to_execute(command_arg, message.channel)

                        if isinstance(command_information, dict):
                            past_messages = [msg async for msg in message.channel.history(limit=5)]
                            conversational_context = "\n".join(
                                f"{msg.author.name} dit : {msg.content}" for msg in reversed(past_messages)
                            )

                            self.console.log(f"✨ Sara réfléchit à une réponse pour : '{message.content}'... ✨")
                            response_text = Speech(api_key, self.console).contextSpeech(message.content, f"NECESSARY INFORMATION: {command_information} - {conversational_context}")
                            self.console.log(f"Réflexion de Sara : {response_text}")
                        elif command_information is None:
                            return
                    else:
                        past_messages = [msg async for msg in message.channel.history(limit=5)]
                        conversational_context = "\n".join(
                        f"{msg.author.name} dit : {msg.content}"
                        for msg in reversed(past_messages)
                        )

                        self.console.log(f"✨ Sara réfléchit à une réponse pour : '{message.content}'... ✨")
                        response_text = Speech(api_key, self.console).contextSpeech(message.content,
                                                                                    f"NECESSARY INFORMATION: {conversational_context}")
                        self.console.log(f"Réflexion de Sara : {response_text}")


                    sara_embed = Embed.create(
                        title="Depuis son poste de travail, Sara répond...",
                        description=response_text,
                        footer_text="Projet Litessera • Lygon",
                    )
                    await message.channel.send(embed=sara_embed)
                    await RandomInteraction(self.console, self.getEnv("OPENAI_API_KEY")).choose_interaction(message, response_text, conversational_context)

        @self.tree.command(name="collect")
        async def collect(interaction: discord.Interaction):
            if interaction.user.id in self.allowed_users:
                await dataCommands(self.console, self.client).collect(interaction)

        @self.tree.command(name="collect_to_text")
        async def collect(interaction: discord.Interaction):
            if interaction.user.id in self.allowed_users:
                await dataCommands(self.console, self.client).collect_to_text(interaction)

        @self.tree.command(name="fx")
        async def f_of_x(interaction: discord.Interaction, function: str):
            await interaction.response.defer()
            await self._graph_2d(function, interaction.channel, interaction)

        @self.tree.command(name="fxy")
        async def f_of_x_y(interaction: discord.Interaction, function: str):
            await interaction.response.defer()
            await self._graph_3d(function, interaction.channel, interaction)

        @self.tree.command(name="simplify")
        async def simplify_expression(interaction: discord.Interaction, expression: str):
            """ Simplifie une expression mathématique en utilisant simplify. """
            await interaction.response.defer()
            await self._simplify(expression, interaction.channel, interaction)

        @self.tree.command(name="polynomial_expansion")
        async def polynomial_expansion(interaction: discord.Interaction, polynomial:str):
            await interaction.response.defer()
            await self._expand_polynomial(polynomial, interaction.channel, interaction)
    def getClient(self):
        return self.client

    def getTree(self):
        return self.tree

    def run(self):
        self.client.run(self.DISCORD_TOKEN)

    def getEnv(self, variable: str) -> str:
        try:
            self.console.log(f"Récupération de la variable d’environnement : {variable}")

            if os.getenv(variable) is None:
                self.console.log("Variable d’environnement non définie.")
                return ""
            env_var = os.environ.get(variable)
            self.console.log(f"Variable acquise : {env_var[:5]}...")
            return env_var
        except Exception as err:
            raise Exception(f"Variable d’environnement {variable} introuvable. - {err.args} : {err}")

    def initializeDatabases(self):
        self.console.log("Initialisation des bases de données.")
        InitializeDatabases(self.console, self.directory).initializeCorte()

    def killDatabases(self):
        self.console.log("Fermeture des bases de données...")
        for db_file in glob.glob("Bot/Data/**/*.db", recursive=True):
            try:
                db = SqliteDatabase(db_file)
                if not db.is_closed():
                    db.close()
                logging.info(f"Base de données fermée : {db_file}")
            except Exception as e:
                self.console.log(f"Échec de la fermeture de la base {db_file} : {e}")

    async def _simplify(self, expression: str, channel: discord.TextChannel, interaction: discord.Interaction = None):
        """Logique principale pour simplifier une expression mathématique."""
        await channel.send(f"Je fais la simplifation de l'expression: {expression}")
        if not expression:
            msg = "Tu dois fournir une expression à simplifier !"
            if interaction:
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await channel.send(msg)
            return

        expression = expression.replace("²", "**2").replace("^", "**")
        try:
            Math.simplify(expression)
            Math.save_latex_to_image(expression, filename="simplified_expression.jpg")

            if interaction:
                await interaction.followup.send(file=discord.File("simplified_expression.jpg"))
            else:
                await channel.send(file=discord.File("simplified_expression.jpg"))
        except Exception as e:
            self.console.log(e)
            error_message = "Je n’ai pas pu simplifier cette fonction. Vérifie ton entrée."
            if interaction:
                await interaction.followup.send(error_message, ephemeral=True)
            else:
                await channel.send(error_message)

    async def _graph_2d(self, function: str, channel: discord.TextChannel, interaction: discord.Interaction = None):
        """Logique principale pour tracer une fonction en 2D."""
        if not function:
            msg = "Tu dois fournir une fonction à tracer !"
            if interaction:
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await channel.send(msg)
            return

        try:
            Graphing(self.console).graph_2d(function)
            if interaction:
                await interaction.followup.send(file=discord.File("graph_2d.jpg"))
            else:
                await channel.send(file=discord.File("graph_2d.jpg"))
        except Exception as e:
            self.console.log(e)
            error_message = "Je n’ai pas pu tracer cette fonction."
            if interaction:
                await interaction.followup.send(error_message, ephemeral=True)
            else:
                await channel.send(error_message)

    async def _graph_3d(self, function: str, channel: discord.TextChannel, interaction: discord.Interaction = None):
        """Logique principale pour tracer une fonction en 3D."""
        if not function:
            msg = "Tu dois fournir une fonction à tracer !"
            if interaction:
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await channel.send(msg)
            return

        function = function.replace("²", "**2")
        try:
            Graphing(self.console).graph_3d(function)
            if interaction:
                await interaction.followup.send(file=discord.File("graph_3d.jpg"))
            else:
                await channel.send(file=discord.File("graph_3d.jpg"))
        except Exception as e:
            self.console.log(e)
            error_message = "Je n’ai pas pu tracer cette fonction. Vérifie les variables ou la syntaxe."
            if interaction:
                await interaction.followup.send(error_message, ephemeral=True)
            else:
                await channel.send(error_message)

    async def _expand_polynomial(self, polynomial: str, channel: discord.TextChannel, interaction: discord.Interaction = None):
        """Expansion de polynomes complexes."""
        if not polynomial:
            msg = "Tu dois fournir une fonction à tracer !"
            if interaction:
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await channel.send(msg)
            return

        function = polynomial.replace("²", "**2")
        function = polynomial.replace("^","**")
        try:
            expanded_polynomial = Math.expand(polynomial)
            Math.save_latex_to_image(expanded_polynomial, filename="expanded_polynomial.jpg")
            if interaction:
                await interaction.followup.send(file=discord.File("expanded_polynomial.jpg"))
            else:
                await channel.send(file=discord.File("expanded_polynomial.jpg"))
        except Exception as e:
            self.console.log(e)
            error_message = "Je n’ai pas pu tracer cette fonction. Vérifie les variables ou la syntaxe."
            if interaction:
                await interaction.followup.send(error_message, ephemeral=True)
            else:
                await channel.send(error_message)

    async def _get_college_information(self):
        return Sigaa().getCurriculum()