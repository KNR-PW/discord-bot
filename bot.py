# #!/usr/bin/env python3
# *_* coding: utf-8 *_*
"""This module deploys discord bot using discord.py library."""

import time
import datetime
import os
from string import Template
import discord
from discord.ext import commands, tasks
from discord.utils import get
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

    current_server = bot.get_guild(
        738142745780027484
    )  # Replace GUILD_ID with the ID of your server
    members = current_server.members
    google_credentials = gspread.service_account(filename="credentials.json")
    sheet = google_credentials.open("Python")
    worksheet_name = "Members"
    worksheet_list = sheet.worksheets()
    worksheet_titles = [w.title for w in worksheet_list]
    if worksheet_name not in worksheet_titles:
        ws_members = sheet.add_worksheet(title=worksheet_name, rows=250, cols=20)
    else:
        ws_members = sheet.worksheet("Members")
    ws_members.update("A1", "nr.")
    ws_members.update("B1", "Member name:")
    ws_members.update("C1", "Member ID:")
    ws_members.update("D1", "Joined server on:")
    ws_members.batch_clear([f"A2:D{len(members)+2}"])
    index = 1
    for member in sorted(members, key=lambda member: member.name):
        ws_members.append_row(
            [index, member.name, member.id, member.created_at.strftime("%d.%b.%Y")],
            table_range="A2",
            value_input_option="RAW",
        )
        index += 1
    print("\nAll members copied")


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
    spreadsheet = google_credentials.open(
        "Python"
    )  # The name of the spredsheet inside ("")
    current_gsheet_a2_value = spreadsheet.sheet1.acell("A2").value
    template = Template(current_gsheet_a2_value)

    server_name = ctx.guild.name
    server_owner = ctx.guild.owner
    server_owner_w_mention = ctx.guild.owner.mention
    member_count = ctx.guild.member_count
    role_test = get(ctx.guild.roles, name="test")
    role_test_w_mention = role_test.mention
    text_channels_count = len(ctx.guild.text_channels)
    voice_channels_count = len(ctx.guild.voice_channels)
    text_channels_list = ", ".join(
        [f"<#{txt_ch.id}>" for txt_ch in ctx.guild.text_channels]
    )
    voice_channels_list = ", ".join(
        [f"<#{v_ch.id}>" for v_ch in ctx.guild.voice_channels]
    )
    creation_date = ctx.guild.created_at.strftime("%b %d %Y")
    role_list = [r.name for r in ctx.guild.roles if r != ctx.guild.default_role]
    role_list_w_mention = [
        r.mention for r in ctx.guild.roles if r != ctx.guild.default_role
    ]
    members_list = ", ".join([m.mention for m in ctx.guild.members])
    members_list_w_mention = ", ".join([m.mention for m in ctx.guild.members])
    server_icon = ctx.guild.icon
    bot_name = bot.user
    message_author = ctx.author.mention

    formated_template = template.substitute(
        server_name=server_name,
        server_owner=server_owner,
        server_owner_w_mention=server_owner_w_mention,
        member_count=member_count,
        role_test_w_mention=role_test_w_mention,
        text_channels_count=text_channels_count,
        voice_channels_count=voice_channels_count,
        text_channels_list=text_channels_list,
        voice_channels_list=voice_channels_list,
        creation_date=creation_date,
        role_list=role_list,
        role_list_w_mention=role_list_w_mention,
        members_list=members_list,
        members_list_w_mention=members_list_w_mention,
        server_icon=server_icon,
        bot_name=bot_name,
        message_author=message_author,
    )

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
    roles = ", ".join(
        [r.mention for r in ctx.guild.roles if r != ctx.guild.default_role]
    )
    embed_1.add_field(
        name="Roles",
        value=roles,
        # value=f'{", ".join([str(r.name) for r in ctx.guild.roles])}'
        inline=False,
    )
    embed_1.set_thumbnail(url=ctx.guild.icon)
    embed_1.set_footer(text="⭐PLACEHOLDER⭐")
    embed_1.set_author(name=f"{ctx.author.name}", icon_url=ctx.message.author.avatar)
    embed_1.add_field(name="Description", value=formated_template, inline=False)
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
        current_gsheet_a2_value = spreadsheet.sheet1.acell("A2").value
        template = Template(current_gsheet_a2_value)
        formated_template = template.substitute(
            server_name=server_name,
            server_owner=server_owner,
            server_owner_w_mention=server_owner_w_mention,
            member_count=member_count,
            role_test_w_mention=role_test_w_mention,
            text_channels_count=text_channels_count,
            voice_channels_count=voice_channels_count,
            text_channels_list=text_channels_list,
            voice_channels_list=voice_channels_list,
            creation_date=creation_date,
            role_list=role_list,
            role_list_w_mention=role_list_w_mention,
            members_list=members_list,
            members_list_w_mention=members_list_w_mention,
            server_icon=server_icon,
            bot_name=bot_name,
            message_author=message_author,
        )
        embed_1.set_field_at(
            6, name="Description", value=formated_template, inline=False
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
        current_gsheet_a2_value = []
        template = []

    update_message.start()


bot.run(os.getenv("DISCORD_TOKEN"))
