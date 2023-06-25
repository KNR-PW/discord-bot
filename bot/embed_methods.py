"""Module containing all the necessary methods for editing embeds."""

from typing import Optional
import discord
from discord.ext import commands
from bot.config_creator import (
    save_to_config_ram,
    read_from_config,
    add_field_value_to_config_ram,
    remove_field_from_config_ram,
)
from bot.message_syntax_functions import convert_string


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
        self,
        new_embed: discord.Embed,
        ctx: commands.Context,
        embed_survey: Optional[discord.ui.Modal] = None,
        update_flag: bool = False,
    ):
        self.embed = new_embed
        self.ctx = ctx
        self.embed_survey = embed_survey
        self.update_flag = update_flag if update_flag is not False else False

    def get_default_embed(self):
        """Sets embed back to default state"""
        self.embed.title = "Title"
        self.embed.description = "None"
        self.embed.set_thumbnail(url="https://knr.edu.pl/images/KNR_log.png")
        self.embed.clear_fields()
        if bool(self.embed.author):
            self.embed.remove_author()
        if bool(self.embed.image):
            self.embed.set_image(url=None)

    async def edit_author(self, interaction: discord.Interaction):
        """Edits the embed's author (name, icon_url, url)."""
        if self.embed_survey is None:
            return
        self.embed_survey.title = "Edit Embed author"
        self.embed_survey.add_item(
            discord.ui.TextInput(
                label="Author Name",
                max_length=100,
                default=self.embed.author.name,
                placeholder="Author name to display in the embed",
                required=False,
            )
        )
        self.embed_survey.add_item(
            discord.ui.TextInput(
                label="Author Icon Url",
                default=self.embed.author.icon_url,
                placeholder="Author icon to display in the embed",
                required=False,
            )
        )
        self.embed_survey.add_item(
            discord.ui.TextInput(
                label="Author Url",
                default=self.embed.author.url,
                placeholder="URL to set as the embed's author link",
                required=False,
            )
        )
        await interaction.response.send_modal(self.embed_survey)
        await self.embed_survey.wait()
        try:
            self.embed.set_author(
                name=str(self.embed_survey.children[0]),
                icon_url=str(self.embed_survey.children[1]),
                url=str(self.embed_survey.children[2]),
            )
            return self.embed
        except discord.HTTPException:
            self.embed.set_author(name=str(self.embed_survey.children[0]))

    async def edit_message(self, interaction: discord.Interaction) -> None:
        """Edits the embed's title and description."""
        embed_description = read_from_config("embed_description")
        if self.embed_survey is None:
            return
        self.embed_survey.title = "Edit Embed message"
        self.embed_survey.add_item(
            discord.ui.TextInput(
                label="Embed Title",
                max_length=255,
                default=self.embed.title,
                placeholder="Title to display in the embed",
                required=False,
            )
        )
        if self.update_flag is False:
            self.embed_survey.add_item(
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
            self.embed_survey.add_item(
                discord.ui.TextInput(
                    label="Embed Description",
                    default=embed_description,
                    placeholder="Description to display in the embed",
                    style=discord.TextStyle.paragraph,
                    required=False,
                    max_length=4000,
                )
            )
        await interaction.response.send_modal(self.embed_survey)
        await self.embed_survey.wait()
        new_embed_description = self.embed_survey.children[1]
        save_to_config_ram(embed_description=str(new_embed_description))
        output_string = convert_string(self.ctx, str(self.embed_survey.children[1]))
        self.embed.title, self.embed.description = (
            str(self.embed_survey.children[0]),
            output_string,
        )

    async def edit_thumbnail(self, interaction: discord.Interaction) -> None:
        """Edits the embed's thumbnail."""
        if self.embed_survey is None:
            return
        self.embed_survey.title = "Edit Embed thumbnail"
        self.embed_survey.add_item(
            discord.ui.TextInput(
                label="Thumbnail Url",
                default=self.embed.thumbnail.url,
                placeholder="Thumbnail you want to display in the embed",
                required=False,
            )
        )
        await interaction.response.send_modal(self.embed_survey)
        await self.embed_survey.wait()
        self.embed.set_thumbnail(url=str(self.embed_survey.children[0]))

    async def edit_image(self, interaction: discord.Interaction) -> None:
        """Edits the embed's image."""
        if self.embed_survey is None:
            return
        self.embed_survey.title = "Edit Embed Image"
        self.embed_survey.add_item(
            discord.ui.TextInput(
                label="Image Url",
                default=self.embed.image.url,
                placeholder="Image you want to display in the embed",
                required=False,
            )
        )
        await interaction.response.send_modal(self.embed_survey)
        await self.embed_survey.wait()
        self.embed.set_image(url=str(self.embed_survey.children[0]))

    async def edit_color(self, interaction: discord.Interaction) -> None:
        """Edits the embed's color"""
        if self.embed_survey is None:
            return
        self.embed_survey.title = "Edit Embed Color"
        self.embed_survey.add_item(
            discord.ui.TextInput(
                label="Embed Color",
                placeholder="The color you want to display on embed (e.g: #303236)",
                max_length=20,
            )
        )
        await interaction.response.send_modal(self.embed_survey)
        await self.embed_survey.wait()
        try:
            color = discord.Colour.from_str(str(self.embed_survey.children[0]))
        except ValueError:
            await interaction.followup.send(
                "Please provide a valid hex code.", ephemeral=True
            )
        else:
            self.embed.colour = color

    async def remove_field(
        self, interaction: discord.Interaction, select: discord.ui.View
    ) -> None:
        """Removes a message field from the embed."""
        if select is None:
            return
        if not self.embed.fields:
            return await interaction.response.send_message(
                "There are no fields to remove.", ephemeral=True
            )
        field_options = []
        for index, field in enumerate(self.embed.fields):
            field_options.append(
                discord.SelectOption(label=str(field.name)[0:30], value=str(index))
            )
        select.children[0].options = field_options
        await interaction.response.send_message(view=select, ephemeral=True)
        await select.wait()

        if vals := select.values:
            for value in vals:
                self.embed.remove_field(int(value))
                remove_field_from_config_ram(int(value), self.embed.fields)

    async def add_field(self, interaction: discord.Interaction) -> None:
        """Adds a message field to the embed."""
        if self.embed_survey is None:
            return
        if len(self.embed.fields) >= 5:
            return await interaction.response.send_message(
                "You can not add more than 5 fields.", ephemeral=True
            )
        self.embed_survey.title = "Add a New Field"
        self.embed_survey.add_item(
            discord.ui.TextInput(
                label="Field Name",
                placeholder="The name you want to display on the field",
                max_length=255,
            )
        )
        self.embed_survey.add_item(
            discord.ui.TextInput(
                label="Field Message",
                max_length=1023,
                style=discord.TextStyle.paragraph,
            )
        )
        self.embed_survey.add_item(
            discord.ui.TextInput(
                label="Field in the same line? (True/False)",
                default="True",
                max_length=5,
                placeholder="The inline for the field either True or False",
            )
        )

        await interaction.response.send_modal(self.embed_survey)
        await self.embed_survey.wait()
        output_string = convert_string(self.ctx, str(self.embed_survey.children[1]))
        try:
            inline = False
            if str(self.embed_survey.children[2]).lower() == "true":
                inline = True
            elif str(self.embed_survey.children[2]).lower() == "false":
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
                name=str(self.embed_survey.children[0]),
                value=output_string,
                inline=inline,
            )
            if self.embed.fields is not None:
                add_field_value_to_config_ram(
                    self.embed.fields, str(self.embed_survey.children[1])
                )
