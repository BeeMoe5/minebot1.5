import discord

import minebot
from creds import TOKEN

bot = minebot.MineBot(
    command_prefix="m!", case_insensitive=True, intents=discord.Intents.all()
)


if __name__ == "__main__":
    bot.run(TOKEN)
