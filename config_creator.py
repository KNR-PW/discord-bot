"""Helper module for creating the `config.ini` configuration file."""
import configparser
import os
from discord.embeds import EmbedProxy


def check_for_config_file() -> None:
    """Checks if `config.ini` exists. If not, creates a default version
    of the `config.ini` file in the root directory."""
    config_file_exists = os.path.exists("config.ini")
    if not config_file_exists:
        config = configparser.ConfigParser()

        config["MessageVariables"] = {
            "embed_channel_id": "None",
            "embed_message_id": "None",
            "embed_description": "None",
        }

        config["FieldsVariables"] = {
            "field_0_value": "None",
            "field_1_value": "None",
            "field_2_value": "None",
            "field_3_value": "None",
            "field_4_value": "None",
        }

        config["MessageRAM"] = {
            "embed_channel_id": "None",
            "embed_message_id": "None",
            "embed_description": "None",
        }

        config["FieldsRAM"] = {
            "field_0_value": "None",
            "field_1_value": "None",
            "field_2_value": "None",
            "field_3_value": "None",
            "field_4_value": "None",
        }

        with open("config.ini", "w", encoding="utf-8") as configfile:
            config.write(configfile)
            print("\nCreated new config.ini file.\n")
    else:
        print("\nFound exisisting config file.\n")


def read_from_config(variable: str) -> str:
    """Reads specified value corresponding to the key from the `config.ini` file.

    Args:
        variable (str): A specific string intended to match
        key of `MessageVariable` section in `config.ini` file.

    Returns:
        str: A value read from `MessageVariables` section from `config.ini`.
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    value = config["MessageVariables"][variable]
    return value


def create_config_ram() -> None:
    """Resets RAM values of `config.ini` file, then copies internal values from
    memory sections to the ram sections."""
    config = configparser.ConfigParser()
    config.read("config.ini")

    reset_section(config, "MessageRAM")
    reset_section(config, "FieldsRAM")
    copy_section(config, "MessageVariables", "MessageRAM")
    copy_section(config, "FieldsVariables", "FieldsRAM")

    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)


def reset_section(config: configparser.ConfigParser, section: str) -> None:
    """Sets selected `config.ini` section values to "None".

    Args:
        config (configparser.ConfigParser): A configuration file (`config.ini`).
        section (str): A selected section within `config.ini` file.
    """
    for key in config[section]:
        config[section][key] = "None"


def copy_section(
    config: configparser.ConfigParser, source_section: str, destination_section: str
) -> None:
    """Copies all values from one `config.ini` section to the other.

    Args:
        config (configparser.ConfigParser): A configuration file (`config.ini`).
        source_section (str): A selected section to copy values from.
        destination_section (str): A selected section to save values to.
    """
    source_values = config.items(source_section)
    for key, value in source_values:
        config[destination_section][key] = value


def save_to_config_ram(**variables: dict[str, str]) -> None:
    """Saves specified varables to `config.ini` file.

    Creates a dictionary that takes one or more items.
    For each items, one must enter the first value that corresponds
    to the key in the `config.ini` file, followed by equal sign and
    the string variable that should be assigned to that key.
    In the next step it writes this variable to a file.

    Args:
        dict[str, str]
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    for key, value in variables.items():
        config["MessageRAM"][key] = str(value)

    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)


def read_field_values_from_config(fields: list[EmbedProxy]) -> list[str]:
    """Reads all fields' values from `FieldsVariables` section of `config.ini` file.
    Saves them into a list.

    Args:
        fields (list[discord.embeds.EmbedProxy]): A list of fields in the
        `discord.Embed` object.

    Returns:
        list[str]: A list containing all fields' values.
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    old_descriptions = []

    values = [f"field_{i}_value" for i in range(len(fields))]

    for value in values:
        description = config["FieldsVariables"][value]
        old_descriptions.append(description)
    return old_descriptions


def add_field_value_to_config_ram(fields: list[EmbedProxy], description: str) -> None:
    """Saves newly created field component to the `config.ini` file.

    Args:
        fields (list[discord.embeds.EmbedProxy]):
        A list of fields in `discord.Embed` object.
        description (str): Description of the last added field.
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    field_num = int(len(fields) - 1)
    key = f"field_{field_num}_value"

    config["FieldsRAM"][key] = str(description)

    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)


def remove_field_from_config_ram(field_number: int, fields: list[EmbedProxy]) -> None:
    """Removes selected field value from the `config.ini` file.

    Matches a number of the last removed embed filed,
    to the field in the `config.ini` file.
    Sets values in the file to "None". Checks the section if there are cases where
    fields contain a user-created description, followed by a field with the description
    "None" and again a field with content. If so, it performs operations to merge the
    fields with the content together, and all the "None" fields were at the end.
    This corresponds to the actual operations when deleting any but the last field
    in the Embed object, where successive fields move in a row relative to the
    last deleted field.

    Args:
        field_number (int): The number corresponding to the field
        that has been removed from the embed.
        fields (list[discord.embeds.EmbedProxy]):A list of fields in
        `discord.Embed` object.
    """
    config = configparser.ConfigParser()
    config.read("config.ini")

    value_to_remove = f"field_{field_number}_value"

    config["FieldsRAM"][value_to_remove] = "None"

    field_dict = config["FieldsRAM"]

    keys = list(field_dict.keys())
    fields_num = len(fields)

    for i, key in enumerate(keys):
        value = field_dict[key]
        if value == "None" and i + 1 <= fields_num:
            next_key = keys[i + 1]
            field_dict[key] = field_dict[next_key]
            field_dict[next_key] = "None"

    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)


def reset_config_ram() -> None:
    """Sets all values of the `MessageRAM`and `FieldsRAM` sections in the `config.ini`
    file to "None".
    """
    config = configparser.ConfigParser()
    config.read("config.ini")

    reset_section(config, "MessageRAM")
    reset_section(config, "FieldsRAM")

    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)


def save_values_from_ram_to_memory() -> None:
    """Saves RAM sections' values to the memory sections in the `config.ini` file.

    Copies all values from the RAM sections to the memory sections.
    Afterwards sets all the values in RAM sections to "None".
    """
    config = configparser.ConfigParser()
    config.read("config.ini")

    copy_section(config, "MessageRAM", "MessageVariables")
    copy_section(config, "FieldsRAM", "FieldsVariables")
    reset_section(config, "MessageRAM")
    reset_section(config, "FieldsRAM")

    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)
