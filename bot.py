#!/usr/bin/env python3
import discord
from discord.ext import commands
from dotenv import load_dotenv
import time
import os

load_dotenv() #loads your local .env file with discord token

class MyClient(discord.Client):
    async def on_ready(self):
        print(f"\nLogged in as {self.user} (ID: {self.user.id}) at {time.strftime('%X')}")
        print('------------------------------')
    

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)

@client.event
async def on_message(message, guild):
    if message.author == client.user: # Stops the bot from replying to itself
        return
    
    print(f'Message from {message.author}: {message.content}')
    
    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')  #Simple reply.
        
    if message.content.startswith('!hello Bot'):
        await message.reply(f'Hello! {message.author}', mention_author=True)  #Reply with replying to user massage.
    

client.run(os.getenv("DISCORD_TOKEN"))