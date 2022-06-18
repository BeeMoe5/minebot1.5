import random

import discord
from discord.ext import commands

import minebot
from creds import TOKEN

bot = minebot.MineBot(
    command_prefix=["m!", "M!"],
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


@bot.command()
async def mega(ctx: commands.Context):
    """Mega"""
    urls = [
        "https://cdn.discordapp.com/attachments/849899889797234688/987138180329377832/F142852C-419E-4823-A93C-8FB2010B5560.png",
        "https://cdn.discordapp.com/attachments/849899889797234688/987138181004677211/51F2ACD2-3AC8-4B4B-9BD1-16546D6E6370.png",
        "https://cdn.discordapp.com/attachments/849899889797234688/987140415943737394/E7E08D6B-036D-4BEF-9E11-8AB1783BA310.jpg",
        "https://media.discordapp.net/attachments/849899889797234688/928852399332946020/A3A7DB15-8714-42A9-9E44-6427CAEE7216.jpg",
        "https://cdn.discordapp.com/attachments/481300027411791885/904543794643476540/IMG_1668.jpg",
        "https://cdn.discordapp.com/attachments/481300027411791885/718149088843005972/20200604_120751.jpg",
        "https://cdn.discordapp.com/attachments/481300027411791885/615939191091626012/Snapchat-1557141170.jpg",
        "https://cdn.discordapp.com/attachments/481300027411791885/577192563136659466/Screenshot_20190512-110105_Snapchat.jpg",
        "https://cdn.discordapp.com/attachments/559541051237335041/987232937583992842/8F23A009-EE62-42BE-870A-1A9599302AB7.jpg",
        "https://cdn.discordapp.com/attachments/559541051237335041/987233795889594389/54AE6649-57D2-4DD5-A2FD-C3A8ADBFC6BD.jpg",
        "https://cdn.discordapp.com/attachments/559541051237335041/987233796560666665/670B875F-D8F2-4D01-A163-E7024EBA15EC.jpg",
        "https://cdn.discordapp.com/attachments/559541051237335041/987234001225936906/4C624323-8894-4005-876E-0BA1C015D9E2.jpg",
        "https://cdn.discordapp.com/attachments/559541051237335041/987234080603136000/57A5A456-D442-4A85-80C9-C91A5B36DCBA.jpg",
        "https://cdn.discordapp.com/attachments/559541051237335041/987234125553479740/B480E2AA-ABE7-4B98-A00B-EDF64F8264B7.jpg",
        "https://cdn.discordapp.com/attachments/559541051237335041/987234250669555722/CA9073D5-2D47-4F00-9598-6E8BC51A68BE.jpg",
        "https://cdn.discordapp.com/attachments/559541051237335041/987234201201954876/A68C1DEC-33D2-4C9A-A435-176DB18FF031.jpg",
        "https://cdn.discordapp.com/attachments/559541051237335041/987233872146210846/7BEEC3EA-F95A-4E4D-8EA5-3C210479DB8B.jpg",
    ]
    await ctx.send(urls[int(len(urls) * random.random())])


if __name__ == "__main__":
    bot.run(TOKEN)
