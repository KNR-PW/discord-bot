"""Module containing classes for creating and managing embed messages using the Embed
Creator."""

import datetime
from typing import List, Optional
from contextlib import suppress
import discord
from discord.ext import commands, tasks
from config_creator import (
    save_to_config_ram,
    read_from_config,
    read_field_values_from_config,
    reset_config_ram,
    save_values_from_ram_to_memory,
)
from message_syntax_functions import convert_string


@tasks.loop(seconds=15)
async def auto_update(
    last_message: discord.message.Message, embed: discord.Embed, ctx: commands.Context
):
    """
    Periodically updates the last sent embed. Looks for changes in embed description.

    Loads the last message sent and its description.
    Re-converts the text of its description to match the current state,
    finally updates the message.

    Args:
        last_message (`discord.message.Message`): last sent message by bot,
        created from the `EmbedCreator`.
        embed (`discord.Embed`): An object from the `Discord.Embed` class that
        will be used as the main embed.
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discoFrd server data; used by discord.ext.commands.
    """
    embed_description = read_from_config("embed_description")
    if embed.fields is not None:
        num_of_fields = len(embed.fields)
        new_descriptions = []
        old_descriptions = read_field_values_from_config(embed.fields)
        for description in old_descriptions:
            new_description = convert_string(ctx, description)
            new_descriptions.append(new_description)
        for i in range(0, num_of_fields):
            embed.set_field_at(
                i,
                name=embed.fields[i].name,
                value=new_descriptions[i],
                inline=embed.fields[i].inline,
            )
    output_string = convert_string(ctx, embed_description)
    embed.description = output_string
    now = datetime.datetime.now()
    embed.set_footer(
        text=f"""Last auto update: {now.strftime('%d.%m.%Y - %H:%M:%S')}"""
    )
    await last_message.edit(embed=embed)


class FieldToRemove(discord.ui.View):
    """
    Subclass of the `discord.ui.View` class. Used for creating a select prompt.

    Args:
        placeholder (str): The placeholder text that will be displayed
        in the channel select menu.
        options (List[SelectOption]): A list of `SelectOption` instances that
        will be displayed as options in the select prompt.
        max_values (int, optional): The maximum number of options
        that can be selected by the user. Default is 1.
        ephemeral (bool, optional): A boolean indicating whether
        the select prompt will be sent as an ephemeral message or not. Default is False.
    """

    def __init__(
        self,
        placeholder: str,
        options: List[discord.SelectOption],
        max_values: int = 1,
        ephemeral: bool = False,
    ) -> None:
        super().__init__()
        self.children[0].placeholder = placeholder
        self.children[0].max_values = max_values
        self.children[0].options = options
        self.values = Optional[List[str]]
        self.ephemeral = ephemeral

    @discord.ui.select()
    async def select_callback(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        """Creates select object that inherits it's atributes from the class."""
        await interaction.response.defer(ephemeral=self.ephemeral)
        if self.ephemeral:
            await interaction.delete_original_response()
        else:
            with suppress(Exception):
                await interaction.message.delete()  # type: ignore
        self.values = select.values
        self.stop()


class ChannelSelectMenu(discord.ui.View):
    """
    Subclass of the `discord.ui.View` class. Used for creating a channel select menu.

    Args:
        placeholder (str): The placeholder text that will be displayed
        in the channel select menu.
        ephemeral (bool, optional): A boolean indicating whether the
        channel select menu will be sent as an ephemeral message or not.
        Default is False.
        max_values (int, optional): The maximum number of options that can be
        selected by the user. Default is 1.
    """

    def __init__(
        self, placeholder: str, ephemeral: bool = False, max_values: int = 1
    ) -> None:
        super().__init__()
        self.values = None
        self.ephemeral = ephemeral
        self.children[0].placeholder, self.children[0].max_values = (  # type: ignore
            placeholder,
            max_values,
        )

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[
            discord.ChannelType.text,
            discord.ChannelType.private_thread,
            discord.ChannelType.public_thread,
            discord.ChannelType.news,
        ],
    )
    async def callback(
        self, interaction: discord.Interaction, select: discord.ui.ChannelSelect
    ):
        """Creates select object that inherits it's atributes from the class."""
        await interaction.response.defer(ephemeral=self.ephemeral)
        if self.ephemeral:
            await interaction.delete_original_response()
        else:
            await interaction.message.delete()  # type: ignore
        self.values = [interaction.guild.get_channel(i.id) for i in select.values]
        self.stop()


class EmbedSurvey(discord.ui.Modal):
    """
    Subclass of the `discord.ui.Modal` class.
    Used for creating modals that require user input.

    Args:
        title (str): The title of the modal.
    """

    def __init__(self, title: str):
        self.title = title
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction, /):
        await interaction.response.defer(ephemeral=True)
        self.stop()


class EditSelectMenu(discord.ui.Select):
    """
    Subclass of the `discord.ui.Select` class.
    Used for creating a select menu to edit embed.

    Args:
        new_embed (`discord.Embed`): An object from the `Discord.Embed` class that
        will be used as the main embed.
        ctx (`discord.ext.commands.Context`): necessary parameter when accesing
        some discord server data. Used by internal methods.
        update_flag (`bool`): A raised flag to indicate whether
        a new embed will be initialized or the previous one updated.
    """

    def __init__(
        self, new_embed: discord.Embed, ctx: commands.Context, update_flag: bool
    ):
        super().__init__(
            placeholder="Expand the list to edit the embed's...",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label="Title and Message",
                    description="Set a title and description for the embed",
                ),
                discord.SelectOption(
                    label="Add Field", description="Add a field to the embed"
                ),
                discord.SelectOption(
                    label="Remove Field", description="Remove a field from the embed"
                ),
                discord.SelectOption(
                    label="Author", description="Set a author for the embed"
                ),
                discord.SelectOption(
                    label="Thumbnail", description="Set a thumbnail for the embed"
                ),
                discord.SelectOption(
                    label="Image", description="Set an image for the embed"
                ),
                discord.SelectOption(
                    label="Color", description="Set a color for the embed"
                ),
            ],
        )
        self.embed, self.ctx, self.update_flag = new_embed, ctx, update_flag

    async def callback(self, interaction):
        options = {
            "Title and Message": "edit_message",
            "Add Field": "add_field",
            "Remove Field": "remove_field",
            "Author": "edit_author",
            "Thumbnail": "edit_thumbnail",
            "Image": "edit_image",
            "Color": "edit_color",
        }
        selected_option = self.values[0]
        from embed_methods import EmbedEditingMethods
        creator_methods = EmbedEditingMethods(self.embed, self.ctx, self.update_flag)
        if selected_option == "Remove Field":
            await creator_methods.remove_field(interaction)
            await interaction.message.edit(embed=self.embed)
        elif selected_option == "Add Field" and len(self.embed.fields) >= 5:
            await creator_methods.add_field(interaction)
            await interaction.message.edit(embed=self.embed)
        elif selected_option in options:
            await getattr(creator_methods, options[selected_option])(interaction)
            if selected_option != "Remove Field" or len(self.embed.fields) < 5:
                await interaction.edit_original_response(embed=self.embed)


class SendButton(discord.ui.Button):
    """
    Subclass of the `discord.ui.Button` class.
    Used for creating a clickable button for deploying embed.

    Args:
        new_embed (`discord.Embed`): An object from the `Discord.Embed` class that
        will be used as the main embed.
        ctx (`discord.ext.commands.Context`): necessary parameter when accesing
        some discord server data. Used by internal methods.
    """

    def __init__(self, new_embed: discord.Embed, ctx: commands.Context):
        self.embed = new_embed
        self.ctx = ctx
        super().__init__(label="Send Embed", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        channel_select_menu = ChannelSelectMenu(
            "Select a channel to send this embed...", True, 1
        )
        await interaction.response.send_message(
            view=channel_select_menu, ephemeral=True
        )
        await channel_select_menu.wait()
        if channel_select_menu.values:
            if not isinstance(
                channel_select_menu.values[0],
                (discord.StageChannel, discord.ForumChannel, discord.CategoryChannel),
            ):
                embed_message = await channel_select_menu.values[0].send(
                    embed=self.embed
                )
                embed_message_id = embed_message.id
                embed_channel_id = channel_select_menu.values[0].id
                save_to_config_ram(
                    embed_channel_id=embed_channel_id, embed_message_id=embed_message_id
                )
                await interaction.message.delete()  # type: ignore
                save_values_from_ram_to_memory()
                if auto_update.is_running():
                    auto_update.restart(embed_message, self.embed, self.ctx)
                else:
                    auto_update.start(embed_message, self.embed, self.ctx)


class UpdateButton(discord.ui.Button):
    """
    Subclass of the `discord.ui.Button` class.
    Used for creating a clickable button for updating embed.

    Args:
        last_embed (`discord.Embed`): An object from the `Discord.Embed` class that
        will be used as the main embed.
        ctx (`discord.ext.commands.Context`): necessary parameter when accesing
        some discord server data. Used by internal methods
        last_message (`discord.message.Message`): last sent message by bot,
        created from the `EmbedCreator`.
    """

    def __init__(
        self,
        last_embed: discord.Embed,
        ctx: commands.Context,
        last_message: discord.message.Message,
    ):
        self.embed = last_embed
        self.ctx = ctx
        self.last_message = last_message
        super().__init__(label="Update Embed", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        embed_message = await self.last_message.edit(embed=self.embed)
        await interaction.message.delete()  # type: ignore
        save_values_from_ram_to_memory()
        auto_update.restart(embed_message, self.embed, self.ctx)


class ResetButton(discord.ui.Button):
    """
    Subclass of the `discord.ui.Button` class.
    Used for creating a clickable button for returning embed to the default state.

    Args:
        new_embed (`discord.Embed`): An object from the `Discord.Embed` class that
        will be used as the main embed.
        ctx (`discord.ext.commands.Context`): necessary parameter when accesing
        some discord server data. Used by internal methods.
    """

    def __init__(self, new_embed: discord.Embed, ctx: commands.Context):
        self.embed = new_embed
        self.ctx = ctx
        super().__init__(label="Reset Embed", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        from embed_methods import EmbedEditingMethods
        creator_methods = EmbedEditingMethods(self.embed, self.ctx)
        creator_methods.get_default_embed()
        reset_config_ram()
        await interaction.response.edit_message(embed=self.embed)


class CancelButton(discord.ui.Button):
    """
    Subclass of the `discord.ui.Button` class.
    Used for creating a clickable button to cancel Embed Creator.

    Args:
        new_embed (`discord.Embed`): An object from the `Discord.Embed` class that
        will be used as the main embed.
        ctx (`discord.ext.commands.Context`): necessary parameter when accesing
        some discord server data. Used by internal methods.
    """

    def __init__(self, new_embed: discord.Embed, ctx: commands.Context):
        self.embed = new_embed
        self.ctx = ctx
        super().__init__(label="Cancel Embed", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()  # type: ignore
        reset_config_ram()


class HelpSelect(discord.ui.Select):
    """
    Subclass of the `discord.ui.Select` class.
    Used for creating a select menu to read embeds.

    Args:
        help_embed (`discord.Embed`): An object from the `Discord.Embed` class that
        will be used as the main embed.
    """

    def __init__(self, help_embed: discord.Embed):
        self.help_embed = help_embed
        self.flag: bool = False

        options = [
            discord.SelectOption(
                label="Commands",
                description="Possible discord commands",
            ),
            discord.SelectOption(
                label="Message Syntax",
                description="How to get more from the text",
            ),
        ]
        super().__init__(
            options=options, max_values=1, placeholder="Learn more about the bot..."
        )

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]

        if selected_option == "Commands":
            content = """
            \n
            :small_orange_diamond:`!help | /help` - Info about the bot.

            :small_orange_diamond:`!embed_creator | /embed_creator` - Embed Creator
            (A tool for dynamic embed building).

            :small_orange_diamond:`!embed_update | /embed_update` -
            opens Embed Creator menu and lets you edit last send embed.

            *For more in-depth information go to:
            https://github.com/KNR-PW/discord-bot*
            """
            self.help_embed.add_field(name="Discord Commands", value=content)

        else:
            syntax1 = """
            \n
            The bot can convert relevant commands in text into valuable information
            when you invoke `/embed_creator` or `!embed_creator` discord commands and
            try to edit either embed description or add and edit a text field.
            When typing the message, commands are recognized inside curly brackets `{}`.

            :small_orange_diamond:`{list_members [...]}` -
            Returns a list of members who have required roles.
            In addition to roles, the text can include
            the logical operators `and`/`or` and `not`.
            """

            syntax2 = """
            :small_orange_diamond:`{count_members [...]}` - Works like list_members,
            but instead of returning names, it returns a number.

            :small_orange_diamond:`{member [...]}` - Returns **@Name**.

            :small_orange_diamond:`{role [...]}` - Returns a single **@Role**.

            :small_orange_diamond:`{text_channel [...]}` - Returns **#TextChannel**.

            :small_orange_diamond:`{voice_channel [...]}` - Returns **@VoiceChannel**.

            **In case of an incorrect argument name in the text, a missing argument,
            or an argument that does not exist, the bot will return `[None]`**.

            *For more in-depth information go to:
            https://github.com/KNR-PW/discord-bot*

            """
            self.help_embed.add_field(name="Message Syntax", value=syntax1)
            self.help_embed.add_field(name="** **", value=syntax2, inline=False)
        if self.flag is False:
            self.flag = True  # First time choosing option
        else:
            if len(self.help_embed.fields) == 2:
                self.help_embed.remove_field(index=0)  # Clicking Twice Commands
            elif len(self.help_embed.fields) == 3:
                if self.help_embed.fields[0].name == "Message Syntax":
                    self.help_embed.remove_field(index=0)
                    self.help_embed.remove_field(index=0)
                else:
                    self.help_embed.remove_field(index=0)
            else:  # Clicking Twice Message Syntax
                self.help_embed.remove_field(index=0)
                self.help_embed.remove_field(index=0)
        await interaction.response.edit_message(embed=self.help_embed)


class HelpMenu(discord.ui.View):
    """
    Subclass of the `discord.ui.View` class.
    It is intended to be used as a base class for creating a panel that allows users
    to read more about the KNR Bot.
    """

    def __init__(self, timeout=60.0):
        self.help_embed = discord.Embed()
        super().__init__(timeout=timeout)
        self.add_item(HelpSelect(self.help_embed))

    async def on_timeout(self):
        self.clear_items()


class EmbedCreator(discord.ui.View):
    """
    Subclass of the `discord.ui.View` class.
    It is intended to be used as a base class for creating a panel that allows users
    to create embeds in a specified Discord TextChannel.

    Args:
        new_embed (`discord.Embed`): An object from the `Discord.Embed` class that
        will be used as the main embed.
        ctx (`discord.ext.commands.Context`): necessary parameter when accesing
        some discord server data. Used by internal methods.
        last_message (`discord.message.Message`): last sent message by bot
        from `EmbedCreator`.
        update_flag (`bool`): A flag that can be raised to indicate whether
        a new embed will be initialized or the previous one updated..
    """

    def __init__(
        self,
        new_embed: discord.Embed,
        ctx: commands.Context,
        last_message: Optional[discord.message.Message] = None,
        update_flag: bool = False,
    ):
        self.embed = new_embed
        self.ctx = ctx
        self.last_message = last_message if last_message is not None else None
        self.update_flag = update_flag if update_flag is not False else False
        super().__init__()
        self.add_item(EditSelectMenu(self.embed, self.ctx, self.update_flag))
        if update_flag is False:
            self.add_item(SendButton(self.embed, self.ctx))
        else:
            self.add_item(UpdateButton(self.embed, self.ctx, self.last_message))
        self.add_item(ResetButton(self.embed, self.ctx))
        self.add_item(CancelButton(self.embed, self.ctx))
