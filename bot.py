# #!/usr/bin/env python3
# *_* coding: utf-8 *_*
"""This module deploys discord bot using discord.py library."""

import time
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()  # loads your local .env file with discord token


#class MyClient(discord.Client):
#    """Represents a client that connects to Discord.
#    This class is used to interact with the Discord WebSocket and API.
#    """
#
#    async def on_ready(self):
#        """Sends notification message when connected to the server."""
#        print(f"\nLogged in as {self.user} (ID: {self.user.id})")
#        print(f"Logging time {time.strftime('%X')}")
#        print("------------------------------")


intents = discord.Intents.default()
intents.message_content = True  # pylint: disable=assigning-non-slot
intents.members = True  # pylint: disable=assigning-non-slot

#client = MyClient(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

#@client.event
#async def on_message(message):
#    """Reads the message from the chat and returns the corresponding message.
#
#    Parameters:
#    message (str): The string sent by the user on Discord chat
#    which the bot listens for. For the bot to respond to the message,
#    it must begin with "!" and be in the list of arguments.
#    Possible arguments are defined by the "message.content.startswith()"
#
#    Returns:
#    str: The type of response is defined by the
#    corresponding message.channel.send()
#    """
#    if message.author == client.user:  # Stops the bot from replying to itself
#        return
#    print(f"Message from {message.author}: {message.content}")

#    if message.content.startswith("!hello"):
#        await message.channel.send("Hello!")  # Simple reply.

#    if message.content.startswith("!hello Bot"):
#        await message.reply(
#            f"Hello! {message.author}", mention_author=True
#        )  # Reply with mentioning the author of the message.

@bot.event
async def on_ready():
    """Sends notification message when connected to the server."""
    print(f"\nLogged in as {bot.user} (ID: {bot.user.id})")
    print(f"Logging time {time.strftime('%X')}")
    print("------------------------------")

@bot.command()
async def hello(ctx):
    await ctx.send('hi')    

@bot.command()
async def server(ctx):
    embed = discord.Embed(title=f"{ctx.guild.name} Info", description="Information of this Server", color=discord.Colour.blue())
    embed.add_field(name='🆔Server ID', value=f"{ctx.guild.id}", inline=True)
    embed.add_field(name='📆Created On', value=ctx.guild.created_at.strftime("%b %d %Y"), inline=True)
    embed.add_field(name='👑Owner', value=f"{ctx.guild.owner}", inline=True)
    embed.add_field(name='👥Members', value=f'{ctx.guild.member_count} Members', inline=True)
    embed.add_field(name='💬Channels', value=f'{len(ctx.guild.text_channels)} Text | {len(ctx.guild.voice_channels)} Voice', inline=True)
    embed.add_field(name='Roles', value=f'{", ".join([str(r.name) for r in ctx.guild.roles])}', inline=True)
    embed.set_thumbnail(url=ctx.guild.icon) 
    embed.set_footer(text="⭐PLACEHOLDER⭐")
    embed.set_author(name=f'{ctx.author.name}', icon_url=ctx.message.author.avatar)
    await ctx.send(embed=embed)


bot.run(os.getenv("DISCORD_TOKEN"))
