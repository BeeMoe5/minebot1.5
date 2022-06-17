import discord

import minebot
from creds import TOKEN

bot = minebot.MineBot(
    command_prefix="m!",
    case_insensitive=True,
    intents=discord.Intents.all(),
)


@bot.command()
async def ping(ctx):
    """Pong!"""
    await ctx.send("Pong!")


@bot.command(usage="<message>")
async def echo(ctx, *, message: str):
    """Echos a message."""
    await ctx.send(message)


if __name__ == "__main__":
    bot.run(TOKEN)
