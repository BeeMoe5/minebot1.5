import discord
from discord.ext import commands

from utils import cooldown, get_item


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["bal"])
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
            description=f"{balance} MineDollar" + ("s" if balance != 1 else ""),
            color=0x00FF00,  # green
        )
        # send the embed
        await ctx.send(embed=embed)

    @commands.group(aliases=["inv"])
    async def inventory(self, ctx: commands.Context):
        """
        Check your inventory.
        """

        if ctx.invoked_subcommand is None:

            # get the user's inventory
            inventory = await self.bot.db.players.find_one({"_id": ctx.author.id})
            if inventory:
                inventory = inventory["inventory"]

            # set up the embed
            embed = discord.Embed(
                title=f"{ctx.author.name}'s inventory",
                color=0x00FF00,  # green
            )

            if not inventory:
                embed.description = "You don't have any items."
                return await ctx.send(embed=embed)

            items = {}
            for item in inventory:
                if item in items:
                    items[item] += 1
                else:
                    items[item] = 1
            # add the items to the embed
            embed.description = ""
            for n, item in enumerate(items.keys(), start=1):
                embed.description += f"{n}. {item.title()} ({items[item]})\n"
            # send the embed
            await ctx.send(embed=embed)

    @inventory.command(usage="<item>")
    async def use(self, ctx: commands.Context, *, item: str):
        """
        Use an item from your inventory.
        """

        # get the user's inventory
        inventory = await self.bot.db.players.find_one({"_id": ctx.author.id})
        if inventory is not None:
            inventory = inventory["inventory"]
        else:
            return await ctx.send("You don't have any items.")
        # get the item
        item = get_item(ctx, item.lower())
        if item is None:
            return await ctx.send("That item is invalid.")
        # check if item in inventory
        if item["name"] not in inventory:
            return await ctx.send("You don't have that item.")
        # check if the item is usable
        if item["usable"] is False:
            return await ctx.send("That item isn't usable.")
        # use the item
        # if the item is a food or drink, remove it from the inventory
        if item["type"] in ["food", "drink"]:
            await self.bot.db.players.update_one(
                {"_id": ctx.author.id},
                {"$pull": {"inventory": item["name"]}},
            )

        # send a message
        await ctx.send(item["use_msg"])

    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx: commands.Context):
        """
        Check the leaderboard.
        """

        # get the leaderboard
        DESCENDING = -1
        # sort by coins
        players = (
            await self.bot.db.players.find().sort("coins", DESCENDING).to_list(None)
        )
        # set up the embed
        embed = discord.Embed(
            title="Leaderboard",
            description="",
            color=0x00FF00,  # green
        )
        # add the leaderboard to the embed
        for n, player in enumerate(players, start=1):
            user = self.bot.get_user(player["_id"])
            embed.description += (
                f"{n}. {user.mention} - {player['coins']} MineDollar"
                + ("s" if player["coins"] != 1 else "")
                + "\n"
            )
        # send the embed
        await ctx.send(embed=embed)

    @cooldown(days=1)
    @commands.command()
    async def daily(self, ctx: commands.Context):
        """
        Get your daily reward.
        """
        # add the daily reward to the user's balance
        await self.bot.db.players.update_one(
            {"_id": ctx.author.id}, {"$inc": {"coins": 7}}, upsert=True
        )
        # send a message
        await ctx.send("You received 7 MineDollar!")


def setup(bot):
    bot.add_cog(Player(bot))
