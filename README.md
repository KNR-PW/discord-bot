<a href="https://knr.edu.pl/">
    <img src="https://knr.edu.pl/images/KNR_log.png" alt="KNR logo" title="KNR" align="right" height="100" />
</a>

# Discord Bot

![GitHub issues](https://img.shields.io/github/issues-raw/KNR-PW/discord-bot)
![GitHub last commit](https://img.shields.io/github/last-commit/KNR-PW/discord-bot)
![GitHub](https://img.shields.io/github/license/KNR-PW/discord-bot)

&nbsp;
<div align="center">

The aim of this project is to create a personalized bot to help with server management on discord, using the `discord.py` library. At the moment the project is in the development phase. Ultimately, the bot is supposed to place provided messages on the text channel, collect data from the server and save it to the google sheet.

[Getting started](#getting-started) •
[Discord Commands](#discord-commands) •
[License](#license) 

</div>
&nbsp;


## Getting started

---

1. Create a Bot account. For this, you can find many tutorials on the web. I personally recommend [this](https://discordpy.readthedocs.io/en/stable/discord.html) or [that one](https://www.androidpolice.com/how-to-make-discord-bot/).

2. Install necessary libraries in terminal:

   ```powershell
   pip install -r requirements.txt
   ```

3. If you decide to run your bot from a personal computer, with only you having access to the code, you can replace `DISCORD_TOKEN`variable inside the quote in the `bot.py` with your token acquired when creating the bot: 

   ```python
   client.run(os.getenv("DISCORD_TOKEN"))
   ```

    Otherwise, it is advised to store your token in a separate file. For this create `.env` file inside the same folder as the `bot.py` file. Inside put following line:

   ```python
   DISCORD_TOKEN="Your token goes here"
   ```

   If you want to place this bot on your github account, before doing so you should create an empty `.gitignore` file, where you should write:

   ```text
   .env
   ```

   This will prevent git from accidentally sending your token for others to see.

4. You can now run your bot. Open a command line and change the directory to the path of your bot files. Next type in the word python, or python3 if you have both versions, followed by the file name of your bot, like this:

   ```text
   python3 bot.py
   ```

## Discord commands

---
This is a list of currently supported commands in the text chat:

```text
!hello - Simple "Hello!" reply in return
!hello Bot - Reply with mentioning to user message
```

## License

---
Copyright © 2022 KNR

This project is [MIT](https://choosealicense.com/licenses/mit/) licenced.
