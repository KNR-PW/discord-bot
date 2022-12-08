# #!/usr/bin/env python3
# *_* coding: utf-8 *_*
"""This module deploys discord bot using discord.py library."""

import time
import os
import discord
from dotenv import load_dotenv


load_dotenv()  # loads your local .env file with discord token


class MyClient(discord.Client):
    """Represents a client that connects to Discord.
    This class is used to interact with the Discord WebSocket and API.
    """

    async def on_ready(self):
        """Sends notification message when connected to the server."""
        print(f"\nLogged in as {self.user} (ID: {self.user.id})")
        print(f"Logging time {time.strftime('%X')}")
        print("------------------------------")


intents = discord.Intents.default()
intents.message_content = True  # pylint: disable=assigning-non-slot


client = MyClient(intents=intents)


@client.event
async def on_message(message):
    """Reads the message from the chat and returns the corresponding message.

    Parameters:
    message (str): The string sent by the user on Discord chat
    which the bot listens for. For the bot to respond to the message,
    it must begin with "!" and be in the list of arguments.
    Possible arguments are defined by the "message.content.startswith()"

    Returns:
    str: The type of response is defined by the
    corresponding message.channel.send()
    """
    if message.author == client.user:  # Stops the bot from replying to itself
        return

    print(f"Message from {message.author}: {message.content}")

    if message.content.startswith("!hello"):
        await message.channel.send("Hello!")  # Simple reply.

    if message.content.startswith("!hello Bot"):
        await message.reply(
            f"Hello! {message.author}", mention_author=True
        )  # Reply with replying to user massage.


client.run(os.getenv("DISCORD_TOKEN"))
