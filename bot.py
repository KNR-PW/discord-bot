#!/usr/bin/env python3
# *_* coding: utf-8 *_*
"""This module deploys discord bot using discord.py library."""

import time
import datetime
import os
from typing import List, Optional
from contextlib import suppress
import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()  # loads your local .env file with the discord token
DISCORD_TOKEN: Optional[str] = os.getenv("DISCORD_TOKEN")

# pylint: disable=invalid-name
embed_channel_id = int()
embed_message_id = int()
embed_description = str()
# pylint: enable=invalid-name


class Bot(commands.Bot):
    """A subclass of the `commands.Bot` class."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.messages = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    # async def setup_hook(self):

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


bot = Bot()
bot.remove_command("help")


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    """Replies with an error message if one occured."""
    print(str(error))
    await ctx.reply(str(error), ephemeral=True)


@tasks.loop(seconds=15)
async def auto_update(ctx: commands.Context, embed_message: discord.message.Message):
    """
    Periodically updates the last sent embed.

    Loads the last message sent and its description.
    Re-converts the text of its description to match the current state,
    finally updates the message.

    Args:
        ctx (discord.ext.commands.context.Context): necessary parameter when
        accesing discord server data; used by discord.ext.commands.
        embed_message (discord.message.Message): message containing last deployed embed.
    """
    output_string = converting_string(ctx, str(embed_description))
    embed = embed_message.embeds[0]
    embed.description = output_string
    now = datetime.datetime.now()
    embed.set_footer(
        text=f"""Last auto update: {now.strftime('%d.%m.%Y - %H:%M:%S')}"""
    )
    await embed_message.edit(embed=embed)


class EmbedEditingMethods:
    """
    A class to be inherited by `EditSelectMenu` class. Stores methods for creating
    the main embed modifying survey and for editing embed itself.

    Args:
        new_embed (`discord.Embed`): An object from the `Discord.Embed` class that
        will be used as the main embed.
        ctx (`discord.ext.commands.Context`): necessary parameter when accesing
        some discord server data. Used by internal methods.
        update_flag (`bool`): A flag that can be raised to indicate whether
        a new embed will be initialized or the previous one updated..
    """

    def __init__(
        self, new_embed: discord.Embed, ctx: commands.Context, update_flag: bool = False
    ):
        self.embed = new_embed
        self.ctx = ctx
        self.update_flag = update_flag if update_flag is not False else False

    def get_default_embed(self):
        """Sets embed back to default state"""
        self.embed.title = "Title"
        self.embed.description = "description"
        self.embed.set_thumbnail(url="https://knr.edu.pl/images/KNR_log.png")
        self.embed.clear_fields()
        if bool(self.embed.author):
            self.embed.remove_author()
        if bool(self.embed.image):
            self.embed.set_image(url=None)

    async def edit_author(self, interaction: discord.Interaction):
        """Edits the embed's author (name, icon_url, url)."""
        embed_survey = EmbedSurvey(title="Edit Embed Author")
        embed_survey.add_item(
            discord.ui.TextInput(
                label="Author Name",
                max_length=100,
                default=self.embed.author.name,
                placeholder="Author name to display in the embed",
                required=False,
            )
        )
        embed_survey.add_item(
            discord.ui.TextInput(
                label="Author Icon Url",
                default=self.embed.author.icon_url,
                placeholder="Author icon to display in the embed",
                required=False,
            )
        )
        embed_survey.add_item(
            discord.ui.TextInput(
                label="Author Url",
                default=self.embed.author.url,
                placeholder="URL to set as the embed's author link",
                required=False,
            )
        )
        await interaction.response.send_modal(embed_survey)
        await embed_survey.wait()
        try:
            self.embed.set_author(
                name=str(embed_survey.children[0]),
                icon_url=str(embed_survey.children[1]),
                url=str(embed_survey.children[2]),
            )
            return self.embed
        except discord.HTTPException:
            self.embed.set_author(name=str(embed_survey.children[0]))

    async def edit_message(self, interaction: discord.Interaction) -> None:
        """Edits the embed's title and description."""
        global embed_description  # pylint: disable=invalid-name
        embed_survey = EmbedSurvey(title="Edit Embed Message")
        embed_survey.add_item(
            discord.ui.TextInput(
                label="Embed Title",
                max_length=255,
                default=self.embed.title,
                placeholder="Title to display in the embed",
                required=False,
            )
        )
        if self.update_flag is False:
            embed_survey.add_item(
                discord.ui.TextInput(
                    label="Embed Description",
                    default=self.embed.description,
                    placeholder="Description to display in the embed",
                    style=discord.TextStyle.paragraph,
                    required=False,
                    max_length=4000,
                )
            )
        else:
            embed_survey.add_item(
                discord.ui.TextInput(
                    label="Embed Description",
                    default=str(embed_description),
                    placeholder="Description to display in the embed",
                    style=discord.TextStyle.paragraph,
                    required=False,
                    max_length=4000,
                )
            )
        await interaction.response.send_modal(embed_survey)
        await embed_survey.wait()
        embed_description = embed_survey.children[1]
        output_string = converting_string(self.ctx, str(embed_survey.children[1]))
        self.embed.title, self.embed.description = (
            str(embed_survey.children[0]),
            output_string,
        )

    async def edit_thumbnail(self, interaction: discord.Interaction) -> None:
        """Edits the embed's thumbnail."""
        embed_survey = EmbedSurvey(title="Edit Embed Thumbnail")
        embed_survey.add_item(
            discord.ui.TextInput(
                label="Thumbnail Url",
                default=self.embed.thumbnail.url,
                placeholder="Thumbnail you want to display in the embed",
                required=False,
            )
        )
        await interaction.response.send_modal(embed_survey)
        await embed_survey.wait()
        self.embed.set_thumbnail(url=str(embed_survey.children[0]))

    async def edit_image(self, interaction: discord.Interaction) -> None:
        """Edits the embed's image."""
        embed_survey = EmbedSurvey(title="Edit Embed Thumbnail")
        embed_survey.add_item(
            discord.ui.TextInput(
                label="Image Url",
                default=self.embed.image.url,
                placeholder="Image you want to display in the embed",
                required=False,
            )
        )
        await interaction.response.send_modal(embed_survey)
        await embed_survey.wait()
        self.embed.set_image(url=str(embed_survey.children[0]))

    async def edit_color(self, interaction: discord.Interaction) -> None:
        """Edits the embed's color"""
        embed_survey = EmbedSurvey(title="Edit Embed Colour")
        embed_survey.add_item(
            discord.ui.TextInput(
                label="Embed Color",
                placeholder="The color you want to display on embed (e.g: #303236)",
                max_length=20,
            )
        )
        await interaction.response.send_modal(embed_survey)
        await embed_survey.wait()
        try:
            color = discord.Colour.from_str(str(embed_survey.children[0]))
        except ValueError:
            await interaction.followup.send(
                "Please provide a valid hex code.", ephemeral=True
            )
        else:
            self.embed.colour = color

    async def remove_field(self, interaction: discord.Interaction) -> None:
        """Removes a message field from the embed."""
        if not self.embed.fields:
            return await interaction.response.send_message(
                "There is no fields to remove.", ephemeral=True
            )
        field_options = list()
        for index, field in enumerate(self.embed.fields):
            field_options.append(
                discord.SelectOption(label=str(field.name)[0:30], value=str(index))
            )
        select = FieldToRemove(
            placeholder="Select a field to remove...",
            options=field_options,
            max_values=len(field_options),
            ephemeral=True,
        )
        await interaction.response.send_message(view=select, ephemeral=True)
        await select.wait()

        if vals := select.values:
            for value in vals:
                self.embed.remove_field(int(value))

    async def add_field(self, interaction: discord.Interaction) -> None:
        """Adds a message field to the embed."""
        if len(self.embed.fields) >= 25:
            return await interaction.response.send_message(
                "You can not add more than 25 fields.", ephemeral=True
            )
        embed_survey = EmbedSurvey(title="Add a new field")
        embed_survey.add_item(
            discord.ui.TextInput(
                label="Field Name",
                placeholder="The name you want to display on the field",
                max_length=255,
            )
        )
        embed_survey.add_item(
            discord.ui.TextInput(
                label="Field Message",
                max_length=1023,
                style=discord.TextStyle.paragraph,
            )
        )
        embed_survey.add_item(
            discord.ui.TextInput(
                label="Field in the same line? (True/False)",
                default="True",
                max_length=5,
                placeholder="The inline for the field either True or False",
            )
        )

        await interaction.response.send_modal(embed_survey)
        await embed_survey.wait()
        output_string = converting_string(self.ctx, str(embed_survey.children[1]))
        try:
            inline = False
            if str(embed_survey.children[2]).lower() == "true":
                inline = True
            elif str(embed_survey.children[2]).lower() == "false":
                inline = False
            else:
                raise ValueError("Bad Bool Input.")
        except ValueError:
            await interaction.followup.send(
                "Please provide a valid input in `inline` either True Or False.",
                ephemeral=True,
            )
        else:
            self.embed.add_field(
                name=str(embed_survey.children[0]), value=output_string, inline=inline
            )


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
        self.values = None
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

    async def on_submit(self, interaction: discord.Interaction):
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

    def __init__(self, new_embed, ctx: commands.Context, update_flag: bool):
        self.embed = new_embed
        self.ctx = ctx
        self.update_flag = update_flag

        options = [
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
        ]
        super().__init__(
            placeholder="Expand the list to edit the embed's...",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]

        creator_methods = EmbedEditingMethods(self.embed, self.ctx, self.update_flag)
        if selected_option == "Title and Message":
            await creator_methods.edit_message(interaction)
        elif selected_option == "Add Field":
            await creator_methods.add_field(interaction)
        elif selected_option == "Remove Field":
            await creator_methods.remove_field(interaction)
            await interaction.message.edit(embed=self.embed)
        elif selected_option == "Author":
            await creator_methods.edit_author(interaction)
        elif selected_option == "Thumbnail":
            await creator_methods.edit_thumbnail(interaction)
        elif selected_option == "Image":
            await creator_methods.edit_image(interaction)
        elif selected_option == "Color":
            await creator_methods.edit_color(interaction)
        if selected_option != "Remove Field":
            await self.update_embed(interaction)

    async def update_embed(self, interaction: discord.Interaction):
        """Updates embed."""
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
                global embed_channel_id  # pylint: disable=invalid-name
                global embed_message_id  # pylint: disable=invalid-name
                embed_message = await channel_select_menu.values[0].send(
                    embed=self.embed
                )
                embed_message_id = embed_message.id
                embed_channel_id = channel_select_menu.values[0].id
                await interaction.message.delete()  # type: ignore
                auto_update.start(self.ctx, embed_message)


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
        auto_update.restart(self.ctx, embed_message)


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
        creator_methods = EmbedEditingMethods(self.embed, self.ctx)
        creator_methods.get_default_embed()
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

            :small_orange_diamond:`!hello` - Greets user.

            :small_orange_diamond:`!embed1` - Text converted with the message syntax.

            :small_orange_diamond:`!server` - Embedded message with the server stats.

            :small_orange_diamond:`!embed_creator | /embed_creator` - Embed Creator
            (A tool for dynamic embed building).

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


@bot.hybrid_command(
    name="embed_creator",
    with_app_command=True,
    description="Create your own embed with Embed Creator",
)
@app_commands.guilds(discord.Object(id=os.getenv("GUILD_ID")))
@commands.has_permissions(administrator=True)
async def embed_creator(ctx: commands.Context):
    """Creates embed and initializes EmbedCreator object.

    Args:
        ctx (`discord.ext.commands.Context`): necessary parameter when accesing
        some discord server data. Used by internal methods.

    """
    new_embed = discord.Embed(title="Title", description="description")
    new_embed.set_thumbnail(url="https://knr.edu.pl/images/KNR_log.png")
    view = EmbedCreator(new_embed, ctx)
    await ctx.send(content="**Preview of the embed:**", view=view, embed=new_embed)


@bot.hybrid_command(
    name="embed_update",
    with_app_command=True,
    description="Edit previously deployed embed",
)
@app_commands.guilds(discord.Object(id=os.getenv("GUILD_ID")))
@commands.has_permissions(administrator=True)
async def embed_update(ctx: commands.Context):
    """Fetches message containing embed and initializes EmbedCreator object.

    Args:
        ctx (`discord.ext.commands.Context`): necessary parameter when accesing
        some discord server data. Used by internal methods.

    """
    try:
        channel = bot.get_channel(embed_channel_id)
        if channel is not None:
            last_message = await channel.fetch_message(embed_message_id)
            last_embed = last_message.embeds[0]
            update_flag = True
            view = EmbedCreator(last_embed, ctx, last_message, update_flag)
            await ctx.send(
                content="**Preview of the embed:**", view=view, embed=last_embed
            )
    except AttributeError:
        await ctx.send("Could not find last embed.")


@bot.hybrid_command(
    name="help",
    with_app_command=True,
    description="Read how to use this bot.",
)
@app_commands.guilds(discord.Object(id=os.getenv("GUILD_ID")))
@commands.has_permissions(administrator=True)
async def bot_help(ctx: commands.Context):
    """Shows the user useful information about the bot.

    Args:
        ctx (`discord.ext.commands.Context`): necessary parameter when accesing
        some discord server data. Used by internal methods.

    """
    view = HelpMenu()
    await ctx.send(view=view)


def finding_single_member(ctx, member_name: str) -> str:
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
        return f"<#{discord_channel.id}>"
    else:
        return "[None]"


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
        edited_string = input_string[start_index + 1 : end_index]  # noqa: E203
        function_string = edited_string.strip()
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


if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN)
else:
    print("Can't find token to access the bot.")
