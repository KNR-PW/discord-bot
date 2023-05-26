"""Helper module for creating the `config.ini` configuration file."""
import configparser
import os


def check_for_config_file():
    """Creates a default version of the `config.ini` file in the root directory."""
    config_file_exists = os.path.exists("config.ini")
    if not config_file_exists:
        config = configparser.ConfigParser()
        config["DEFAULT"] = {
            "embed_channel_id": "False",
            "embed_message_id": "False",
            "embed_description": "False",
        }

        config["GlobalVariables"] = {
            "embed_channel_id": "False",
            "embed_message_id": "False",
            "embed_description": "False",
        }

        with open("config.ini", "w", encoding="utf-8") as configfile:
            config.write(configfile)
        print("\nCreated new config.ini file.\n")
    else:
        print("\nFound exisisting config file.\n")


def save_to_config(**variables):
    """Saves specified varables to `config.ini` file."""
    config = configparser.ConfigParser()
    config.read("config.ini")
    for key, value in variables.items():
        config["GlobalVariables"][key] = str(value)
    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)


def read_from_config(variable):
    """Reads specified varable from `config.ini` file."""
    config = configparser.ConfigParser()
    config.read("config.ini")
    value = config["GlobalVariables"][variable]
    return value