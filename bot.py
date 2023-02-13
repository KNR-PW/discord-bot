# #!/usr/bin/env python3
# *_* coding: utf-8 *_*
"""This module deploys discord bot using discord.py library."""

import time
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


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
async def count_members(ctx, *, role_names_str: str):
    """Reads the message from the chat and returns the number of members
    that meet the conditions.

    Reads the message if the message starts with the "command_prefix"
    (that was set in when initializing commands.Bot object) and the name
    in the title of the method. Returns str in "ctx.send()".
    """
    only_nots_in_str = False
    if "not " in role_names_str:
        if role_names_str.startswith("not "):
            role_names = role_names_str.replace(" ", "")
            role_names = role_names.split("not")
            only_nots_in_str = True
            not_role_names = [
                role
                for role in role_names[1:]
                if " not " not in role or "not " not in role
            ]
        else:
            # two types of operations
            role_names = role_names_str.split(" not ")
            only_nots_in_str = False
            not_role_names = [role for role in role_names[1:] if " not " not in role]
        not_roles = []
        for not_role_name in not_role_names:
            not_role = discord.utils.get(ctx.guild.roles, name=not_role_name)
            if not_role is not None:
                not_roles.append(not_role)
            else:
                await ctx.send(
                    f"Could not find `{not_role_name}` role. Check spelling."
                )
                return
        not_roles = [role for role in not_roles if role is not None]
        role_names_str = role_names[0]
    else:
        not_roles = []

    if only_nots_in_str is False:
        role_names = (
            role_names_str.split(" and ")
            if " and " in role_names_str
            else role_names_str.split(" or ")
        )
        roles = []
        for role_name in role_names:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role is not None:
                roles.append(role)
            else:
                await ctx.send(f"Could not find `{role_name}` role. Check spelling.")
                return
        roles = [role for role in roles if role is not None]
        if not roles:
            await ctx.send("Could not find one or more roles. Check spelling.")
            return

    members = set()
    if " and " in role_names_str:
        role_names = " and ".join(role.name for role in roles)
        for role in roles:
            if not members:  # start if members is empty
                members.update(role.members)
            else:
                members &= set(role.members)
    elif " or " in role_names_str:
        role_names = " or ".join(role.name for role in roles)
        for role in roles:
            if not members:  # start if members is empty
                members.update(role.members)
            else:
                members &= set(role.members)
    else:
        role_names = role_names[0]
        members = set(ctx.guild.members)

    for not_role in not_roles:
        members -= set(not_role.members)

    num_members = len(members)
    not_role_names = ", ".join(not_role.name for not_role in not_roles)
    if not_roles:
        if only_nots_in_str is True:
            await ctx.send(
                f"There are {num_members} members without roles `{not_role_names}`."
            )
        else:
            await ctx.send(
                f"There are {num_members} members with the roles `{role_names}`"
                f" but not the roles `{not_role_names}`."
            )
    else:
        await ctx.send(
            f"There are {num_members} members with the roles `{role_names}`."
        )


@bot.command()
async def list_members(ctx, *, role_names_str: str):
    """Reads the message from the chat and returns the list of the members
    that meet the conditions.

    Reads the message if the message starts with the "command_prefix"
    (that was set in when initializing commands.Bot object) and the name
    in the title of the method. Returns str in "ctx.send()".
    """
    only_nots_in_str = False
    if "not " in role_names_str:
        if role_names_str.startswith("not "):
            role_names = role_names_str.replace(" ", "")
            role_names = role_names.split("not")
            only_nots_in_str = True
            not_role_names = [
                role
                for role in role_names[1:]
                if " not " not in role or "not " not in role
            ]
        else:
            # two types of operations
            role_names = role_names_str.split(" not ")
            only_nots_in_str = False
            not_role_names = [role for role in role_names[1:] if " not " not in role]
        not_roles = []
        for not_role_name in not_role_names:
            not_role = discord.utils.get(ctx.guild.roles, name=not_role_name)
            if not_role is not None:
                not_roles.append(not_role)
            else:
                await ctx.send(
                    f"Could not find `{not_role_name}` role. Check spelling."
                )
                return
        not_roles = [role for role in not_roles if role is not None]
        role_names_str = role_names[0]
    else:
        not_roles = []

    if only_nots_in_str is False:
        role_names = (
            role_names_str.split(" and ")
            if " and " in role_names_str
            else role_names_str.split(" or ")
        )
        roles = []
        for role_name in role_names:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role is not None:
                roles.append(role)
            else:
                await ctx.send(f"Could not find `{role_name}` role. Check spelling.")
                return
        roles = [role for role in roles if role is not None]
        if not roles:
            await ctx.send("Could not find one or more roles. Check spelling.")
            return

    members = set()
    if " and " in role_names_str:
        role_names = " and ".join(role.name for role in roles)
        for role in roles:
            if not members:  # start if members is empty
                members.update(role.members)
            else:
                members &= set(role.members)
    elif " or " in role_names_str:
        role_names = " or ".join(role.name for role in roles)
        for role in roles:
            if not members:  # start if members is empty
                members.update(role.members)
            else:
                members &= set(role.members)
    else:
        role_names = role_names[0]
        members = set(ctx.guild.members)

    for not_role in not_roles:
        members -= set(not_role.members)

    members = list(members)
    member_names = ", ".join(member.mention for member in members)
    not_role_names = ", ".join(not_role.name for not_role in not_roles)
    if not_roles:
        if only_nots_in_str is True:
            await ctx.send(
                f"The members without roles `{not_role_names}` are: {member_names}."
            )
        else:
            await ctx.send(
                f"The members with the roles `{role_names}`"
                f" but not the roles `{not_role_names}` are: {member_names}."
            )
    else:
        await ctx.send(
            f"The members with the roles `{role_names}` are: {member_names}."
        )


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
    embed_1.add_field(name="Description", value="123", inline=False)
    await ctx.send(embed=embed_1)


bot.run(os.getenv("DISCORD_TOKEN"))
