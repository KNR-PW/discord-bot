# #!/usr/bin/env python3
# *_* coding: utf-8 *_*
"""This module deploys discord bot using discord.py library."""

import time
import os
import discord
from dotenv import load_dotenv


load_dotenv()  # loads your local .env file with discord token

intents = discord.Intents.default()
intents.message_content = True  # pylint: disable=assigning-non-slot


client = MyClient(intents=intents)

bot = commands.Bot(command_prefix="!", intents=intents)


    print(f"Message from {message.author}: {message.content}")


@bot.command()
async def hello(ctx):
    """Reads the message from the chat and returns the corresponding message.

    Reads the message if the message starts with the "command_prefix"
    that was set in when initializing commands.Bot object and ends with
    the name in the title of the method. Returns str in "ctx.send()".
    """
    await ctx.send("hi")


@bot.command()
async def server(ctx):
    """Reads the message from the chat and returns
    embeded message with server stats.

    Reads the message if the message starts with the "command_prefix"
    that was set in when initializing commands.Bot object and ends with
    the name in the title of the method. Returns str in "ctx.send()".

    Parameters in the embeded message:
    - Server name and desription
    - Server ID number
    - Server creation date
    - Server owner
    - Number of members
    - Number of text and voice channels
    - List of roles on the server
    - Server icon
    - Footer message
    - Message anuthor and his icon.
    """
    embed = discord.Embed(
        title=f"{ctx.guild.name} Info",
        description="Information of this Server",
        color=discord.Colour.blue())
    embed.add_field(
        name="🆔Server ID",
        value=f"{ctx.guild.id}",
        inline=True)
    embed.add_field(
        name="📆Created On",
        value=ctx.guild.created_at.strftime("%b %d %Y"),
        inline=True)
    embed.add_field(
        name="👑Owner",
        value=f"{ctx.guild.owner}",
        inline=True)
    embed.add_field(
        name="👥Members",
        value=f"{ctx.guild.member_count} Members",
        inline=True)
    em_t_channels = len(ctx.guild.text_channels)
    em_v_channels = len(ctx.guild.voice_channels)
    embed.add_field(
        name="💬Channels",
        value=f"{em_t_channels} Text | {em_v_channels} Voice",
        inline=True,)
    embed.add_field(
        name="Roles",
        value=f'{", ".join([str(r.name) for r in ctx.guild.roles])}',
        inline=True)
    embed.set_thumbnail(url=ctx.guild.icon)
    embed.set_footer(text="⭐PLACEHOLDER⭐")
    embed.set_author(
        name=f"{ctx.author.name}",
        icon_url=ctx.message.author.avatar)
    await ctx.send(embed=embed)


client.run(os.getenv("DISCORD_TOKEN"))
