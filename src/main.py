import discord

import minebot
from creds import TOKEN
from discord.ext import commands

bot = minebot.MineBot(
    command_prefix="m!",
    case_insensitive=True,
    intents=discord.Intents.all(),
)


@bot.command()
async def ping(ctx: commands.Context):
    """Pong!"""
    await ctx.send("Pong!")


@bot.command(usage="<message>")
async def echo(ctx: commands.Context, *, message: str):
    """Echos a message."""
    await ctx.send(message)


@bot.command(name="eval", usage="<code>", hidden=True)
@commands.is_owner()
async def _eval(ctx: commands.Context, *, code: str):
    """Runs Python code."""
    code = code.replace("```py", "").replace("```", "")
    code = "\n".join(f"    {i}" for i in code.splitlines())
    body = f"async def func():\n{code}"
    context = {
        "bot": bot,
        "ctx": ctx,
        "message": ctx.message,
        "author": ctx.author,
        "channel": ctx.channel,
        "guild": ctx.guild,
        "discord": discord,
    }
    try:
        exec(body, context)
        func = context["func"]
        res = await func()
        if res is not None:
            await ctx.send(res)
    except Exception as e:
        await ctx.send(f"```py\n{e}\n```")


if __name__ == "__main__":
    bot.run(TOKEN)
