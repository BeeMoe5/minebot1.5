import random

import discord
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def chance(self, ctx: commands.Context):
        """
        Try your luck at a chance game.
        If the emojis are the same, you win.
        """

        # dictionary of the possible symbols and coins they represent
        symbols = {
            ":cherries:": 1,
            ":banana:": 2,
            ":apple:": 2,
            ":grapes:": 3,
            ":tangerine:": 2,
            ":moneybag:": 6,
            ":gem:": 8,
            ":heart:": 10,
            ":clubs:": 4,
            ":spades:": 6,
        }
        emojis = list(symbols.keys())

        chance = random.randint(1, 100)
        win = chance <= 25

        if win:
            slot_1 = slot_2 = slot_3 = random.choice(emojis)
            title = ":tada:" * 2 + "**You won!**" + ":tada:" * 2
            color = 0x00FF00  # green
            coins = symbols[slot_1]
        else:
            # make it so the slots don't match
            while True:
                slot_1 = random.choice(emojis)
                slot_2 = random.choice(emojis)
                slot_3 = random.choice(emojis)
                if slot_1 != slot_2 and slot_2 != slot_3 and slot_3 != slot_1:
                    break

            title = "**You lost!**"
            color = 0xFF0000  # red
            coins = 0

        coin_msg = (
            f"You won {coins} coin" + ("s" if coins != 1 else "") + "!"
            if coins != 0
            else "You didn't win any coins."
        )
        if coins == 10:
            coin_msg += "\nlove is the most expensive gift in the world."

        # set up the embed
        embed = discord.Embed(
            title=title,
            description=coin_msg,
            color=color,
        )

        # add the slots to the embed
        embed.add_field(
            name="Slot 1",
            value=slot_1,
            inline=True,
        )
        embed.add_field(
            name="Slot 2",
            value=slot_2,
            inline=True,
        )
        embed.add_field(
            name="Slot 3",
            value=slot_3,
            inline=True,
        )
        # send the embed
        await ctx.send(embed=embed)
        # add the coins to the user's balance
        await self.bot.db.players.update_one(
            {"_id": ctx.author.id}, {"$inc": {"coins": coins}}, upsert=True
        )

    @commands.command()
    async def balance(self, ctx: commands.Context):
        """
        Check your balance.
        """

        # get the user's balance
        balance = await self.bot.db.players.find_one({"_id": ctx.author.id})
        if balance is not None:
            balance = balance["coins"]
        else:
            balance = 0
        # set up the embed
        embed = discord.Embed(
            title=f"{ctx.author.name}'s balance",
            description=f"{balance} coin" + ("s" if balance != 1 else ""),
            color=0x00FF00,  # green
        )
        # send the embed
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Games(bot))
