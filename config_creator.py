"""Helper module for creating the `config.ini` configuration file."""
import configparser


def create_config_file():
    """Creates a default version of the `config.ini` file in the root directory."""
    config = configparser.ConfigParser()
    config["DEFAULT"] = {
        "embed_channel_id": "False",
        "embed_message_id": "False",
        "embed_description": "False",
    }

    config["GlobalVars"] = {
        "embed_channel_id": "False",
        "embed_message_id": "False",
        "embed_description": "False",
    }

    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)
