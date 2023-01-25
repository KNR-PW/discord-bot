# #!/usr/bin/env python3
# *_* coding: utf-8 *_*
"""This module deploys discord bot using discord.py library."""

import time
import datetime
import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import gspread


load_dotenv()  # loads your local .env file with discord token

intents = discord.Intents.default()
intents.message_content = True  # pylint: disable=assigning-non-slot
intents.members = True  # pylint: disable=assigning-non-slot

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Sends notification message when connected to the server."""
    print(f"\nLogged in as {bot.user} (ID: {bot.user.id})")
    print(f"Logging time {time.strftime('%X')}")
    print("-----------------------------------")


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

    Parameters in the embed_1ed message:
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
    now = datetime.datetime.now()

    google_credentials = gspread.service_account(filename="credentials.json")
    spreadsheet = google_credentials.open("Python")
    current_gsheet_a1_value = spreadsheet.sheet1.acell("A1").value

    embed_1 = discord.Embed(
        title=f"{ctx.guild.name} Info",
        description="Information of this Server",
        color=discord.Colour.blue(),
    )
    embed_1.add_field(name="🆔Server ID", value=f"{ctx.guild.id}", inline=True)
    embed_1.add_field(
        name="📆Created On", value=ctx.guild.created_at.strftime("%b %d %Y"), inline=True
    )
    embed_1.add_field(name="👑Owner", value=f"{ctx.guild.owner}", inline=True)
    embed_1.add_field(
        name="👥Members", value=f"{ctx.guild.member_count} Members", inline=True
    )
    em_t_channels = len(ctx.guild.text_channels)
    em_v_channels = len(ctx.guild.voice_channels)
    embed_1.add_field(
        name="💬Channels",
        value=f"{em_t_channels} Text | {em_v_channels} Voice",
        inline=True,
    )
    rolelist = [r.mention for r in ctx.guild.roles if r != ctx.guild.default_role]
    roles = ", ".join(rolelist)
    embed_1.add_field(
        name="Roles",
        value=roles,
        # value=f'{", ".join([str(r.name) for r in ctx.guild.roles])}'
        inline=False,
    )
    embed_1.set_thumbnail(url=ctx.guild.icon)
    embed_1.set_footer(text="⭐PLACEHOLDER⭐")
    embed_1.set_author(name=f"{ctx.author.name}", icon_url=ctx.message.author.avatar)
    embed_1.add_field(
        name="Description", value=f"""{current_gsheet_a1_value}""", inline=False
    )
    embed_1.add_field(
        name="Last Updated:",
        value=f"""This message auto-checks for changes every 15 seconds.
    Last checked: {now.strftime('%Y-%m-%d, %H:%M:%S')}""",
        inline=False,
    )

    update = await ctx.send(embed=embed_1)

    @tasks.loop(seconds=15.0)
    async def update_message():
        now = datetime.datetime.now()
        current_gsheet_a1_value = spreadsheet.sheet1.acell("A1").value
        embed_1.set_field_at(
            6, name="Description", value=f"{current_gsheet_a1_value}", inline=False
        )
        embed_1.set_field_at(
            7,
            name="Last Updated:",
            value=f"""This message auto-checks for changes every 15 seconds.
        Last checked: {now.strftime('%Y-%m-%d, %H:%M:%S')}""",
            inline=False,
        )
        await update.edit(embed=embed_1)
        now = []
        current_gsheet_a1_value = []

    update_message.start()


bot.run(os.getenv("DISCORD_TOKEN"))
