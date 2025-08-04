import glob
import logging
import os
import random
import re

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
from peewee import SqliteDatabase
from rich.console import Console
from sympy import SympifyError

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
            # Plotting and Info
            "fx": self._graph_2d,
            "fxy": self._graph_3d,
            "get_college_information": self._get_college_information,

            # Symbolic Algebra
            "simplify": self._simplify,
            "expand": self._expand_polynomial,
            "factor": self._factor_expression,
            "solve": self._solve_equation,

            # Calculus
            "diff": self._differentiate,
            "integrate": self._integrate,
            "limit": self._calculate_limit,

            # Matrix Operations
            "det": self._matrix_determinant,
            "inv": self._matrix_inverse,
            "eigenvals": self._matrix_eigenvals,

            # Utility
            "to_image": self._save_to_image,
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
                "brianna" in message.content.lower() or
                f"<@{self.client.user.id}>" in message.content or "clairemont" in message.content
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
                                f"{msg.author.name} says : {msg.content}" for msg in reversed(past_messages)
                            )

                            self.console.log(f"✨ Brianna réfléchit à une réponse pour : '{message.content}'... ✨")
                            response_text = Speech(api_key, self.console).contextSpeech(message.content, f"NECESSARY INFORMATION: {command_information} - {conversational_context}")
                            self.console.log(f"Réflexion de Brianna : {response_text}")
                        elif command_information is None:
                            return
                    else:
                        past_messages = [msg async for msg in message.channel.history(limit=5)]
                        conversational_context = "\n".join(
                        f"{msg.author.name} dit : {msg.content}"
                        for msg in reversed(past_messages)
                        )

                        self.console.log(f"✨ Brianna réfléchit à une réponse pour : '{message.content}'... ✨")
                        response_text = Speech(api_key, self.console).contextSpeech(message.content,
                                                                                    f"NECESSARY INFORMATION: {conversational_context}")
                        self.console.log(f"Réflexion de Brianna : {response_text}")


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

        @self.tree.command(name="simplify", description="Simplifie une expression mathématique.")
        async def simplify_expression(interaction: discord.Interaction, expression: str):
            await interaction.response.defer()
            await self._simplify(expression, interaction.channel, interaction)

        @self.tree.command(name="expand", description="Développe une expression polynomiale.")
        async def expand_polynomial_command(interaction: discord.Interaction, polynomial: str):
            await interaction.response.defer()
            await self._expand_polynomial(polynomial, interaction.channel, interaction)

        @self.tree.command(name="factor", description="Factorise une expression mathématique.")
        async def factor_expression_command(interaction: discord.Interaction, expression: str):
            await interaction.response.defer()
            await self._factor_expression(expression, interaction.channel, interaction)

        @self.tree.command(name="solve", description="Résout une équation pour une variable (ex: x**2 - 1).")
        async def solve_equation_command(interaction: discord.Interaction, equation: str, variable: str = "x"):
            await interaction.response.defer()
            await self._solve_equation(equation, channel=interaction.channel, interaction=interaction,
                                       variable=variable)

        @self.tree.command(name="diff", description="Dérive une expression par rapport à une variable.")
        async def differentiate_command(interaction: discord.Interaction, expression: str, variable: str = "x"):
            await interaction.response.defer()
            await self._differentiate(expression, channel=interaction.channel, interaction=interaction,
                                      variable=variable)

        @self.tree.command(name="integrate", description="Intègre une expression par rapport à une variable.")
        async def integrate_command(interaction: discord.Interaction, expression: str, variable: str = "x"):
            await interaction.response.defer()
            await self._integrate(expression, channel=interaction.channel, interaction=interaction, variable=variable)

        @self.tree.command(name="limit", description="Calcule la limite d'une expression.")
        async def limit_command(interaction: discord.Interaction, expression: str, variable: str, point: str):
            await interaction.response.defer()
            await self._calculate_limit(expression, channel=interaction.channel, interaction=interaction,
                                        variable=variable, point=point)

        @self.tree.command(name="det", description="Calcule le déterminant d'une matrice.")
        async def det_command(interaction: discord.Interaction, matrix: str):
            await interaction.response.defer()
            await self._matrix_determinant(matrix, interaction.channel, interaction)

        @self.tree.command(name="inv", description="Calcule l'inverse d'une matrice.")
        async def inv_command(interaction: discord.Interaction, matrix: str):
            await interaction.response.defer()
            await self._matrix_inverse(matrix, interaction.channel, interaction)

        @self.tree.command(name="eigenvals", description="Trouve les valeurs propres d'une matrice.")
        async def eigenvals_command(interaction: discord.Interaction, matrix: str):
            await interaction.response.defer()
            await self._matrix_eigenvals(matrix, interaction.channel, interaction)

        # --- Bot Setup Methods ---

    def getClient(self):
        return self.client

    def getTree(self):
        return self.tree

    def run(self):
        self.client.run(self.DISCORD_TOKEN)

    def getEnv(self, variable: str) -> str:
        try:
            env_var = os.environ.get(variable)
            return "" if env_var is None else env_var
        except Exception as err:
            raise Exception(f"Variable d’environnement {variable} introuvable. - {err.args} : {err}")

    def initializeDatabases(self):
        self.console.log("Initialisation des bases de données.")
        InitializeDatabases(self.console, self.directory).initializeCorte()

    # --- Helper & Command Logic Methods ---
    def _prepare_expression(self, expression: str) -> str:
        """Cleans and formats a math expression string for sympy."""
        if not isinstance(expression, str): return ""
        # Replace common characters
        expr = expression.replace("²", "**2").replace("^", "**")
        # Add explicit multiplication operator for expressions like 'x2' -> 'x**2'
        # This regex finds a letter followed by one or more digits and inserts '**'
        expr = re.sub(r'([a-zA-Z])([0-9]+)', r'\1**\2', expr)
        return expr

    async def _send_math_result(self, result, filename, channel, interaction):
        """Helper function to save and send math results as images."""
        if "Error" in str(result):
            error_message = str(result)
        else:
            try:
                if isinstance(result, dict):
                    formatted_result = ", ".join(
                        [f"\\lambda_{{{i + 1}}} = {val}" for i, val in enumerate(result.keys())])
                else:
                    formatted_result = str(result)
                Math.save_latex_to_image(formatted_result, filename=filename)
                file = discord.File(filename)
                if interaction:
                    await interaction.followup.send(file=file)
                else:
                    await channel.send(file=file)
                return
            except Exception as e:
                self.console.log(f"Error in _send_math_result: {e}")
                error_message = "Je n'ai pas pu générer une image pour ce résultat."
        if interaction:
            await interaction.followup.send(error_message, ephemeral=True)
        else:
            await channel.send(error_message)

    # --- Private Command Implementations ---
    async def _execute_math_command(self, math_function, expression, filename, channel, interaction, *args, **kwargs):
        """Generic executor for math commands to reduce code duplication."""
        if not expression:
            msg = "Vous devez fournir une expression."
            if interaction:
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await channel.send(msg)
            return

        try:
            prepared_expression = self._prepare_expression(expression)
            result = math_function(prepared_expression, *args, **kwargs)
            await self._send_math_result(result, filename, channel, interaction)
        except SympifyError:
            error_message = f"Je n'ai pas pu comprendre l'expression : `{expression}`. Assurez-vous d'utiliser une notation valide comme `x**2` ou `x^2`."
            if interaction:
                await interaction.followup.send(error_message, ephemeral=True)
            else:
                await channel.send(error_message)
        except Exception as e:
            self.console.log(f"An unexpected error occurred in {math_function.__name__}: {e}")
            error_message = "Une erreur inattendue est survenue."
            if interaction:
                await interaction.followup.send(error_message, ephemeral=True)
            else:
                await channel.send(error_message)

    async def _simplify(self, expression: str, channel: discord.TextChannel, interaction: discord.Interaction = None):
        await self._execute_math_command(Math.simplify, expression, "simplified.jpg", channel, interaction)

    async def _expand_polynomial(self, polynomial: str, channel: discord.TextChannel,
                                 interaction: discord.Interaction = None):
        await self._execute_math_command(Math.expand, polynomial, "expanded.jpg", channel, interaction)

    async def _factor_expression(self, expression: str, channel: discord.TextChannel,
                                 interaction: discord.Interaction = None):
        await self._execute_math_command(Math.factor, expression, "factored.jpg", channel, interaction)

    async def _solve_equation(self, equation: str, channel: discord.TextChannel,
                              interaction: discord.Interaction = None, variable: str = "x"):
        await self._execute_math_command(Math.solve_equation, equation, "solved.jpg", channel, interaction, variable)

    async def _differentiate(self, expression: str, channel: discord.TextChannel,
                             interaction: discord.Interaction = None, variable: str = "x"):
        await self._execute_math_command(Math.differentiate, expression, "differentiated.jpg", channel, interaction,
                                         variable)

    async def _integrate(self, expression: str, channel: discord.TextChannel, interaction: discord.Interaction = None,
                         variable: str = "x"):
        await self._execute_math_command(Math.integrate, expression, "integrated.jpg", channel, interaction, variable)

    async def _calculate_limit(self, expression: str, channel: discord.TextChannel,
                               interaction: discord.Interaction = None, variable: str = 'x', point: str = '0'):
        await self._execute_math_command(Math.calculate_limit, expression, "limit.jpg", channel, interaction, variable,
                                         point)

    async def _matrix_determinant(self, matrix_str: str, channel: discord.TextChannel,
                                  interaction: discord.Interaction = None):
        await self._execute_math_command(Math.matrix_determinant, matrix_str, "determinant.jpg", channel, interaction)

    async def _matrix_inverse(self, matrix_str: str, channel: discord.TextChannel,
                              interaction: discord.Interaction = None):
        await self._execute_math_command(Math.matrix_inverse, matrix_str, "inverse.jpg", channel, interaction)

    async def _matrix_eigenvals(self, matrix_str: str, channel: discord.TextChannel,
                                interaction: discord.Interaction = None):
        await self._execute_math_command(Math.matrix_eigenvals, matrix_str, "eigenvals.jpg", channel, interaction)

    async def _save_to_image(self, expression: str, channel: discord.TextChannel,
                             interaction: discord.Interaction = None):
        await self._execute_math_command(lambda expr: expr, expression, "saved_image.jpg", channel, interaction)

    async def _graph_2d(self, function: str, channel: discord.TextChannel, interaction: discord.Interaction = None):
        if not function:
            msg = "Vous devez fournir une fonction à tracer !"
            if interaction:
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await channel.send(msg)
            return
        try:
            prepared_function = self._prepare_expression(function)
            Graphing(self.console).graph_2d(prepared_function)
            file = discord.File("graph_2d.jpg")
            if interaction:
                await interaction.followup.send(file=file)
            else:
                await channel.send(file=file)
        except Exception as e:
            self.console.log(e)
            error_message = "Je n'ai pas pu tracer cette fonction. Vérifiez la syntaxe."
            if interaction:
                await interaction.followup.send(error_message, ephemeral=True)
            else:
                await channel.send(error_message)

    async def _graph_3d(self, function: str, channel: discord.TextChannel, interaction: discord.Interaction = None):
        if not function:
            msg = "Vous devez fournir une fonction à tracer !"
            if interaction:
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await channel.send(msg)
            return
        try:
            prepared_function = self._prepare_expression(function)
            Graphing(self.console).graph_3d(prepared_function)
            file = discord.File("graph_3d.jpg")
            if interaction:
                await interaction.followup.send(file=file)
            else:
                await channel.send(file=file)
        except Exception as e:
            self.console.log(e)
            error_message = "Je n'ai pas pu tracer cette fonction. Vérifiez vos variables et votre syntaxe."
            if interaction:
                await interaction.followup.send(error_message, ephemeral=True)
            else:
                await channel.send(error_message)

    async def _get_college_information(self):
        return Sigaa().getCurriculum()
