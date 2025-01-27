import random

import discord


def default_embed(title, description):
    embed = discord.Embed(
        title=f"{title}",
        description=f"{description}",
        color=discord.Color.purple()  # Purple color for the embed
    )

    embed.set_image(url="https://media1.tenor.com/m/NzpAfsky9lEAAAAd/my-dress-up-darling-anime.gif")
    embed.set_footer(text="Atendente da Taverna da Sara, Sara Delacroix")
    return embed

def whois_embed(name, description, avatar):
    embed = discord.Embed(
        title=f"Entrada n°{random.randint(0,99999)}: {name}",
        description=f"{description}",
        color=discord.Color.purple()
    )

    embed.set_image(url=f"{avatar}")
    embed.set_footer(text="Empire of Lygon Surveillance System")
    return embed