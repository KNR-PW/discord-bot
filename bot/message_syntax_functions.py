"""Module containing functions for converting text inside the Embed Creator
messages."""

import discord


def find_single_member(ctx, member_name: str) -> str:
    """Takes the string and returns the corresponding member from the discord server.

    Each name on the discord server looks like this: name#XXXX,
    where "XXXX" is any 4-digit number. The function reads the entire string,
    finds where the # symbol is, treats it as a dividing line to create
    two new strings, which are used to look up the formatted member's name
    from the server's database.

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


def find_single_role(ctx, rolename: str) -> str:
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


def find_single_text_channel(ctx, channel_name: str) -> str:
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
        return f"<#{discord_channel.id}>"
    return "[None]"


def find_single_voice_channel(ctx, channel_name: str) -> str:
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
        return f"<#{discord_channel.id}>"
    return "[None]"


def search_for_roles(ctx, separated_names_from_str: list, list_for_names: list) -> list:
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
        list: A list of discord roles or an empty list.
    """
    for role_name in separated_names_from_str:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role is not None:
            list_for_names.append(role)
        else:
            list_for_names.clear()
            return list_for_names
    return list_for_names


def create_set_of_roles(
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
        not_roles = search_for_roles(ctx, not_role_names_list, not_roles)
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
        roles = search_for_roles(ctx, role_names_list, roles)
        if not roles:
            final_converted_str = "[None]"
            return final_converted_str

    members = create_set_of_roles(
        ctx, message_core_str, roles, not_roles, only_nots_in_str
    )
    return members


def count_members(ctx, message_core_str: str) -> str:
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


def list_members(ctx, message_core_str: str) -> str:
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


def convert_string(ctx, input_string: str) -> str:
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
        edited_string = input_string[start_index + 1 : end_index]  # noqa: E203
        function_string = edited_string.strip()
        if function_string.startswith("list_members "):
            message_core_str = function_string[13:]
            final_converted_str = list_members(ctx, message_core_str)
        elif function_string.startswith("count_members "):
            message_core_str = function_string[14:]
            final_converted_str = count_members(ctx, message_core_str)
        elif function_string.startswith("role "):
            message_core_str = function_string[5:]
            final_converted_str = find_single_role(ctx, message_core_str)
        elif function_string.startswith("member "):
            message_core_str = function_string[7:]
            final_converted_str = find_single_member(ctx, message_core_str)
        elif function_string.startswith("text_channel "):
            message_core_str = function_string[13:]
            final_converted_str = find_single_text_channel(ctx, message_core_str)
        elif function_string.startswith("voice_channel "):
            message_core_str = function_string[14:]
            final_converted_str = find_single_voice_channel(ctx, message_core_str)
        else:
            final_converted_str = "{" + function_string + "}"
        output_string += final_converted_str
        end_index += 1
    return output_string
