import random

import discord
from discord.ext import commands


class GamesAndEconomy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_item(self, item_name):
        for isle, isle_items in self.bot.shop_items.items():
            for item in isle_items:
                if item_name == item["name"]:
                    return item
        return None

    @commands.command()
    async def chance(self, ctx: commands.Context):
        """
        Try your luck at a chance game.
        If the emojis are the same, you win.
        You will win as low as 1 and as high as 10 MineDollars.
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
        }  # type: dict[str, int]
        emojis = list(symbols.keys())

        chance = random.randint(1, 100)
        win = chance <= 25

        if win:
            slot_1 = slot_2 = slot_3 = random.choice(emojis)
            title = ":tada:" * 2 + "**You won!**" + ":tada:" * 2
            color = 0x00FF00  # green
            coins: int = symbols[slot_1]
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
            coins: int = 0

        coin_msg = (
            f"You won {coins} MineDollar" + ("s" if coins != 1 else "") + "!"
            if coins != 0
            else "You didn't win any MineDollars."
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
            {"_id": ctx.author.id}, {"$inc": {"coins": int(coins)}}, upsert=True
        )

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

    @commands.group()
    async def shop(self, ctx: commands.Context):
        """
        Check the shop.
        """

        if ctx.invoked_subcommand is None:

            # set up the embed
            embed = discord.Embed(
                title="Shop",
                description="Here is the shop.",
                color=0x00FF00,  # green
            )
            # add the items to the embed
            for isle, isle_items in self.bot.shop_items.items():
                items = [f"{item['name']} - {item['price']}" for item in isle_items]
                embed.add_field(
                    name=isle,
                    value="\n".join(items),
                    inline=False,
                )
            # send the embed
            await ctx.send(embed=embed)

    @shop.command(usage="<item>")
    async def buy(self, ctx: commands.Context, item: str):
        """
        Buy an item from the shop.
        """

        # get the user's balance
        balance = await self.bot.db.players.find_one({"_id": ctx.author.id})
        if balance is not None:
            balance = balance["coins"]
        else:
            return await ctx.send("You don't have any MineDollars.")
        # get the item
        item = self.get_item(item.lower())
        if item is None:
            return await ctx.send("That item isn't in the shop.")
        # check if the user has enough money
        if item["price"] > balance:
            return await ctx.send("You don't have enough MineDollars.")
        # subtract the price from the user's balance
        await self.bot.db.players.update_one(
            {"_id": ctx.author.id}, {"$inc": {"coins": int(-item["price"])}}
        )
        # add the item to the user's inventory
        await self.bot.db.players.update_one(
            {"_id": ctx.author.id}, {"$push": {"inventory": item["name"]}}, upsert=True
        )
        # send a message
        await ctx.send(f"You bought {item['name']}!")

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
    async def use(self, ctx: commands.Context, item: str):
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
        item = self.get_item(item.lower())
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


def setup(bot):
    bot.add_cog(GamesAndEconomy(bot))
