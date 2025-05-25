import discord
import random
from typing import List, Tuple, Optional

class Embed:
    """
    A utility class to easily create and return Discord embed objects.
    """
    @staticmethod
    def create(
        title: str,
        description: str = "",
        color: Optional[int] = None,
        fields: Optional[List[Tuple[str, str, bool]]] = None,
        footer_text: Optional[str] = None,
        thumbnail_url: Optional[str] = None

    ) -> discord.Embed:
        """
        Creates and returns a discord.Embed object with random colors if not specified.

        Args:
            title (str): The title of the embed.
            description (str, optional): The main text of the embed. Defaults to "".
            color (Optional[int], optional): The color of the embed's side strip, as an integer. 
                                             If None, a random color is chosen. Defaults to None.
            fields (Optional[List[Tuple[str, str, bool]]], optional): 
                                             A list of fields to add. Each field should be a tuple 
                                             containing (name, value, inline_boolean). Defaults to None.
            footer_text (Optional[str], optional): Text to display at the bottom of the embed. 
                                                   Defaults to None.
            thumbnail_url (Optional[str], optional): URL for the embed's thumbnail image. 
                                                     Defaults to None.

        Returns:
            discord.Embed: The fully constructed embed object.
        """
        # If no color is provided, generate a random hex color code as an integer
        if color is None:
            random_color = random.randint(0, 0xFFFFFF)
        else:
            random_color = color

        # Create the base embed with the core components
        embed = discord.Embed(
            title=title,
            description=description,
            color=random_color
        )

        if fields:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

        if footer_text:
            embed.set_footer(text=footer_text)

        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        return embed