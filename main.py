#!/usr/bin/env python3
# *_* coding: utf-8 *_*
"""This module deploys discord bot using discord.py library."""

import time
import os
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from config_creator import (
    check_for_config_file,
    create_config_ram,
    read_from_config,
    save_values_from_ram_to_memory,
)
from but_gui import EmbedCreator, HelpMenu, auto_update

load_dotenv()  # loads your local .env file with the discord token
DISCORD_TOKEN: Optional[str] = os.getenv("DISCORD_TOKEN")


class Bot(commands.Bot):
    """
    A subclass of the `commands.Bot` class.
    The main class that initializes and operates the bot on the server.
    """

    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.messages = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        """Sends notification message when connected to the server."""
        print(f"\nLogged in as {self.user} (ID: {self.user.id})")
        print(f"Logging time {time.strftime('%X')}")
        print("-----------------------------------")
        try:
            synced = await self.tree.sync(
                guild=discord.Object(id=os.getenv("GUILD_ID"))
            )
            print(f"Synced {len(synced)} slash commands for {self.user}.")
        except Exception as errors:  # pylint: disable=broad-exception-caught
            print(errors)
        await self.setup()

    async def setup(self):
        """
        Reads data from the `config.ini`, recalls the last sent message,
        runs `auto_update`.

        Checks if `config.ini` contains data to retrieve
        the last message sent by the bot.
        Recalls the message from this data and runs `auto_update`.
        In case of failure, it informs about the reason of the problem
        and overwrites the `False` value with all data from the `config.ini` file.
        """
        print("\nAttempting to retrieve last message.")
        await self.wait_until_ready()
        try:
            embed_channel_id = read_from_config("embed_channel_id")
            embed_message_id = read_from_config("embed_message_id")
            channel = await self.fetch_channel(embed_channel_id)
        except (discord.NotFound, discord.HTTPException):
            print("\nChannel Not Found. Resetting values in config.ini.")
            save_values_from_ram_to_memory()
            return
        try:
            last_message = await channel.fetch_message(embed_message_id)
            embed = last_message.embeds[0]
            ctx = await self.get_context(last_message)
            auto_update.start(last_message, embed, ctx)
        except (discord.NotFound, discord.HTTPException):
            print("\nMessage not Found. Resetting values in config.ini.")
            save_values_from_ram_to_memory()
            return
        print("\nLast message found successfully. Automatic refresh started.")


check_for_config_file()

bot = Bot()
bot.remove_command("help")


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    """Replies with an error message if one occured."""
    print(str(error))
    await ctx.reply(str(error), ephemeral=True)


@bot.hybrid_command(
    name="embed_creator",
    with_app_command=True,
    description="Create your own embed with Embed Creator",
)
@app_commands.guilds(discord.Object(id=os.getenv("GUILD_ID")))
@commands.check_any(
    commands.has_guild_permissions(manage_roles=True),
    commands.has_guild_permissions(view_audit_log=True),
)
async def embed_creator(ctx: commands.Context):
    """Creates embed and initializes EmbedCreator object.

    Args:
        ctx (`discord.ext.commands.Context`): necessary parameter when accesing
        some discord server data. Used by internal methods.

    """
    new_embed = discord.Embed(title="Title", description="None")
    new_embed.set_thumbnail(url="https://knr.edu.pl/images/KNR_log.png")
    view = EmbedCreator(new_embed, ctx)
    await ctx.send(content="**Preview of the embed:**", view=view, embed=new_embed)


@bot.hybrid_command(
    name="embed_update",
    with_app_command=True,
    description="Edit previously deployed embed",
)
@app_commands.guilds(discord.Object(id=os.getenv("GUILD_ID")))
@commands.check_any(
    commands.has_guild_permissions(manage_roles=True),
    commands.has_guild_permissions(view_audit_log=True),
)
async def embed_update(ctx: commands.Context):
    """Fetches message containing embed and initializes EmbedCreator object.

    Args:
        ctx (`discord.ext.commands.Context`): necessary parameter when accesing
        some discord server data. Used by internal methods.

    """
    try:
        embed_channel_id = int(read_from_config("embed_channel_id"))
        channel = bot.get_channel(embed_channel_id)
        if channel is not None:
            try:
                embed_message_id = int(read_from_config("embed_message_id"))
                last_message = await channel.fetch_message(embed_message_id)
            except (AttributeError, ValueError):
                await ctx.send("Could not find last embed.")
            else:
                create_config_ram()
                last_embed = last_message.embeds[0]
                update_flag = True
                view = EmbedCreator(last_embed, ctx, last_message, update_flag)
                await ctx.send(
                    content="**Preview of the embed:**", view=view, embed=last_embed
                )
    except (AttributeError, ValueError):
        await ctx.send("Could not find last embed.")


@bot.hybrid_command(
    name="help",
    with_app_command=True,
    description="Read how to use this bot.",
)
@app_commands.guilds(discord.Object(id=os.getenv("GUILD_ID")))
@commands.check_any(
    commands.has_guild_permissions(manage_roles=True),
    commands.has_guild_permissions(view_audit_log=True),
)
async def bot_help(ctx: commands.Context):
    """Shows the user useful information about the bot.

    Args:
        ctx (`discord.ext.commands.Context`): necessary parameter when accesing
        some discord server data. Used by internal methods.

    """
    view = HelpMenu()
    await ctx.send(view=view)


if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN)
else:
    print("Can't find token to access the bot.")
