#!/usr/bin/env python3
# *_* coding: utf-8 *_*
"""This module deploys discord bot using discord.py library."""

import time
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # loads your local .env file with the discord token


intents = discord.Intents(guilds=True, members=True, messages=True)

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    """Sends notification message when connected to the server."""
    print(f"\nLogged in as {bot.user} (ID: {bot.user.id})")
    print(f"Logging time {time.strftime('%X')}")
    print("-----------------------------------")


@bot.command()
async def hello(ctx):
    """Reads the message from the chat. Returns the corresponding message.

    Reads the message if the message starts with the "command_prefix"
    that was set when initializing commands.Bot object and ends with
    the name in the title of the method. Returns str in "ctx.send()".
    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
    Returns:
        discord.message.Message
    """

    await ctx.send("hi")


def finding_single_member(ctx, member_name: str) -> str:
    """Takes the string and returns the corresponding member from the discord server.

    Each name on the discord server looks like this: name#XXXX,
    where "XXXX" is any 4-digit number. The function reads the entire string,
    finds where the # symbol is, treats it as a dividing line to create two new strings,
    which are used to look up the formatted member's name from the server's database.

    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
        member_name (str): A string representing a member to be searched for.
    Returns:
        str: A string with the mentioned role name from the discord server.
    """
    start_index = member_name.find("#")
    name = member_name[:start_index]
    discriminator = member_name[start_index + 1 :]  # noqa: E203
    discord_member = discord.utils.get(
        ctx.guild.members, name=f"{name}", discriminator=f"{discriminator}"
    )
    if discord_member is not None:
        discord_member = discord_member.mention
    else:
        discord_member = "[None]"
    return discord_member


def finding_single_role(ctx, rolename: str) -> str:
    """Takes the string and returns the corresponding role from the discord server.

    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
        rolename (str): A string representing a role to be searched for.
    Returns:
        str: A string with the mentioned role name from the discord server.
    """
    discord_role = discord.utils.get(ctx.guild.roles, name=f"{rolename}")
    if discord_role is not None:
        discord_role = discord_role.mention
    else:
        discord_role = "[None]"
    return discord_role


def finding_single_text_channel(ctx, channel_name: str) -> str:
    """Takes the string and returns the corresponding text channel from the
    discord server.

    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
        channel_name (str): A string representing a text channel name
        to be searched for.
    Returns:
        str: A string with the text channel from the discord server.
    """
    discord_channel = discord.utils.get(ctx.guild.text_channels, name=f"{channel_name}")
    if discord_channel is not None:
        print(type(discord_channel))
        return f"<#{discord_channel.id}>"
    else:
        return "[None]"


def finding_single_voice_channel(ctx, channel_name: str) -> str:
    """Takes the string and returns the corresponding voice channel from the
    discord server.

    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
        channel_name (str): A string representing a voice channel name
        to be searched for.
    Returns:
        str: A string with the voice channel from the discord server.
    """
    discord_channel = discord.utils.get(
        ctx.guild.voice_channels, name=f"{channel_name}"
    )
    if discord_channel is not None:
        print(type(discord_channel))
        return f"<#{discord_channel.id}>"
    else:
        return "[None]"


# channel = discord.utils.get(ctx.guild.channels, name=given_name)


def searching_for_roles(
    ctx, separated_names_from_str: list, list_for_names: list
) -> list:
    """Take the list of names and return the list of discord roles.

    Each name in the list of names is checked for occurrence in the discord server.
    If at least one of the names isn't matched to the roles available
    in the discord server, it returns an empty string, otherwise, a new list of matched
    roles is generated.

    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
        separated_names_from_str (list): A list of names to be checked for
        compatibility.
    Returns:
        list : A list of discord roles or an empty list.
    """
    for role_name in separated_names_from_str:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role is not None:
            list_for_names.append(role)
        else:
            list_for_names.clear()
            return list_for_names
    return list_for_names


def creating_set_of_roles(
    ctx,
    message_core_str: str,
    roles: list,
    not_roles: list,
    only_nots_in_str: bool,
) -> set:
    """Gets a list of roles and, based on met criteria,
    passes matching members into a set.

    Checks the first part of the initial string, split by the "not" operator,
    to see if it contains "and" or " "or" operators. If not, it checks if there was
    a previously raised flag indicating there is a single role in the string or
    one role and at least one "not" operator after. According to these criteria,
    it creates a set with members that have corresponding roles.
    Finally, it removes members whose roles had the "not" operator in the message.

    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
        message_core_str (str) : A string that may contain roles and logical operators
        roles (list): A list of roles that may contain "and" or "or" operators.
        not_roles (list): A list of roles with a "not" operator.
        only_nots_in_str (bool): A flag that tells if the initial message consists
        solely of "not" operators followed by roles.
    Returns:
        set: A set of discord server members.
    """
    members: set = set()
    if " and " in message_core_str:
        for role in roles:
            if not members:  # start if members is empty
                members.update(role.members)
            else:
                members &= set(role.members)
    elif " or " in message_core_str:
        for role in roles:
            members.update(role.members)
    elif only_nots_in_str is False:  # only one positive role
        role = roles[0]
        members.update(role.members)
    else:  # only negative roles
        members = set(ctx.guild.members)

    for not_role in not_roles:
        members -= set(not_role.members)
    return members


def role_searching_core(ctx, message_core_str: str) -> set | str:
    """Analyzes the message, breaks it down into smaller fragments,
    and creates a list of roles.

    Splits a text message into potential roles using the logical "not" operators
    as a dividing line. Calls a subfunction and checks if any roles presenton the
    server are next to "not". Then it does the same for the "and" or "or" operators.
    Creates role lists for each operator. If there are any errors in the message,
    it returns a text message. In the last step, it calls a subfunction that creates
    the final list of all roles corresponding to the logical sentence.

    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
        message_core_str (str): A string that may contain roles and logical operators
    Returns:
        set: A set of discord server members.
        str: A string containing final parsed message.
    """
    only_nots_in_str = False
    roles: list = []
    if "not " in message_core_str:
        if message_core_str.startswith("not "):
            role_names_str = message_core_str.replace(" ", "")
            role_names_list = role_names_str.split("not")
            only_nots_in_str = True
            not_role_names_list = [
                role
                for role in role_names_list[1:]
                if " not " not in role or "not " not in role
            ]
        else:
            # two types of operations
            role_names_list = message_core_str.split(" not ")
            only_nots_in_str = False
            not_role_names_list = [
                role for role in role_names_list[1:] if " not " not in role
            ]
        not_roles: list = []
        not_roles = searching_for_roles(ctx, not_role_names_list, not_roles)
        if not not_roles:
            final_converted_str = "[None]"
            return final_converted_str
        message_core_str = role_names_list[0]
    else:
        not_roles = []

    if only_nots_in_str is False:
        role_names_list = (
            message_core_str.split(" and ")
            if " and " in message_core_str
            else message_core_str.split(" or ")
        )
        roles = []
        roles = searching_for_roles(ctx, role_names_list, roles)
        if not roles:
            final_converted_str = "[None]"
            return final_converted_str

    members = creating_set_of_roles(
        ctx, message_core_str, roles, not_roles, only_nots_in_str
    )
    return members


def counting_members(ctx, message_core_str: str) -> str:
    """Gets a string. Returns either a string with a number of members or a message.

    Calls a subfunction. Checks whether the returned variable is a string or a list.
    If it's the latter, it combines the list's items into one string.
    Finally, it returns the resulting string.

    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
        message_core_str (str): A string that may contain roles and logical operators
    Returns:
        str: A string containing final parsed message.
    """
    members_set_or_message_str = role_searching_core(ctx, message_core_str)
    if isinstance(members_set_or_message_str, str):
        final_converted_str = members_set_or_message_str
    else:
        members = members_set_or_message_str
        num_members = len(members)
        final_converted_str = str(num_members)
    return final_converted_str


def listing_members(ctx, message_core_str: str) -> str:
    """Gets a string. Returns either a string with members names or a message.

    Calls a subfunction. Checks whether the returned variable is a string or a list.
    If it's the latter, it combines the list's items into one string.
    Finally, it returns the resulting string.

    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
        message_core_str (str): A string that may contain roles and logical operators
    Returns:
        str: A string containing final parsed message.
    """
    members_set_or_message_str = role_searching_core(ctx, message_core_str)
    if isinstance(members_set_or_message_str, str):
        final_converted_str = members_set_or_message_str
    else:
        members_set = members_set_or_message_str
        members_list = []
        for member in members_set:
            members_list.append(member.mention)
        member_names = ", ".join(member for member in members_list)
        final_converted_str = member_names
    return final_converted_str


def converting_string(ctx, input_string: str) -> str:
    """Searches for the functional field in a string and based on the condition,
    passes it to the other functions.

    Gets a message string. Searches for "{" and "}" each representing the beginning
    and end of the text to be parsed. Everything inside the braces ("{}")
    is assigned to the new variable. In the next step, the text inside the variable
    is checked to see if it starts with the correct string. If so, the text inside
    the variable is shortened by the length of the part being checked and assigned
    to the next variable, and the appropriate function is called. Finally, the function
    returns the result of the subfunction, which is text.

    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
        input_string (str): A string that may contain curly brackets ({})
    Returns:
        str: A string containing final parsed message.
    """
    output_string = ""
    start_index = 0
    end_index = 0
    while start_index < len(input_string):
        start_index = input_string.find("{", end_index)
        if start_index == -1:
            output_string += input_string[end_index:]
            break
        output_string += input_string[end_index:start_index]
        end_index = input_string.find("}", start_index)
        if end_index == -1:
            output_string += input_string[start_index:]
            break
        function_string = input_string[start_index + 1 : end_index]  # noqa: E203
        if function_string.startswith("list_members "):
            message_core_str = function_string[13:]
            final_converted_str = listing_members(ctx, message_core_str)
            output_string += final_converted_str
        elif function_string.startswith("count_members "):
            message_core_str = function_string[14:]
            final_converted_str = counting_members(ctx, message_core_str)
            output_string += final_converted_str
        elif function_string.startswith("role "):
            message_core_str = function_string[5:]
            final_converted_str = finding_single_role(ctx, message_core_str)
            output_string += final_converted_str
        elif function_string.startswith("member "):
            message_core_str = function_string[7:]
            final_converted_str = finding_single_member(ctx, message_core_str)
            output_string += final_converted_str
        elif function_string.startswith("text_channel "):
            message_core_str = function_string[13:]
            final_converted_str = finding_single_text_channel(ctx, message_core_str)
            output_string += final_converted_str
        elif function_string.startswith("voice_channel "):
            message_core_str = function_string[14:]
            final_converted_str = finding_single_voice_channel(ctx, message_core_str)
            output_string += final_converted_str
        else:
            output_string += "{" + function_string + "}"
        end_index += 1
    return output_string


@bot.command()
async def embed(ctx):
    """Produces a discord embed from a modified string created in itself.

    Takes a string from within itself. Passes it into a parsing function.
    The result of the second function is passed then into a newly created
    discord embed object.

    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
    Returns:
        discord.embeds.Embed: A discord.embeds.Embed object with the parsed message.
    """
    input_string = """
    {text_channel ogólny}
    {voice_channel ogólny}
    """
    output_string = converting_string(ctx, input_string)

    simple_embed = discord.Embed()
    simple_embed.add_field(name="", value=f"{output_string}", inline=True)
    await ctx.send(embed=simple_embed)


@bot.command()
async def server(ctx):
    """Reads the message from the chat and returns
    embedded message with server stats.

    Reads the message if the message starts with the "command_prefix"
    that was set in when initializing commands.Bot object and ends with
    the name in the title of the method. Returns str in "ctx.send()".

    Parameters in the embed_1 message:
    - Server name and description
    - Server ID number
    - Server creation date
    - Server owner
    - Number of members
    - Number of text and voice channels
    - List of roles on the server
    - Server icon
    - Footer message
    - Message the author and his icon.

    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
    Returns:
        discord.embeds.Embed - A discord.embeds.Embed class with the parsed message.
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
