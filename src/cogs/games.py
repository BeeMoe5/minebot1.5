import random

import discord
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def chance(self, ctx):
        """
        Try your luck at a chance game.
        If the emojis are the same, you win.
        """
        # make a list of the possible symbols
        emojis = [
            ":cherries:",
            ":banana:",
            ":apple:",
            ":grapes:",
            ":tangerine:",
            ":moneybag:",
            ":gem:",
            ":heart:",
            ":clubs:",
            ":spades:",
        ]

        chance = random.randint(1, 100)
        win = chance <= 25

        if win:
            slot_1 = slot_2 = slot_3 = random.choice(emojis)
            description = ":tada:" * 2 + "**You won!**" + ":tada:" * 2
            color = 0x00FF00  # green
        else:
            # make it so the slots don't match
            while True:
                slot_1 = random.choice(emojis)
                slot_2 = random.choice(emojis)
                slot_3 = random.choice(emojis)
                if slot_1 != slot_2 and slot_2 != slot_3 and slot_3 != slot_1:
                    break

            description = "**You lost!**"
            color = 0xFF0000  # red

        # set up the embed
        embed = discord.Embed(
            description=description,
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


def setup(bot):
    bot.add_cog(Games(bot))
