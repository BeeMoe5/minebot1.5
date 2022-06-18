import asyncio
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

    def get_pet(self, pet_type):
        for pet in self.bot.pet_shop_items:
            if pet_type == pet["type"]:
                return pet
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
        win = chance <= 15

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
                items = [
                    f"{item['name']} - {item['price']} MineDollar" + "s"
                    if item["price"] != 1
                    else ""
                    for item in isle_items
                ]
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

    @commands.group(name="petshop", aliases=["pshop"])
    async def pet_shop(self, ctx: commands.Context):
        """
        Check the pet shop.
        """
        if ctx.invoked_subcommand is None:
            # set up the embed
            embed = discord.Embed(
                title="Pet Shop",
                description="",
                color=0x00FF00,  # green
            )
            # add the items to the description
            for item in self.bot.pet_shop_items:
                embed.description += (
                    f"{item['emoji']} {item['type'].capitalize()} - {item['price']} MineDollar"
                    + ("s" if item["price"] != 1 else "")
                    + "\n"
                )
            # send the embed
            await ctx.send(embed=embed)

    @pet_shop.command(usage="<pet>")
    async def buy(self, ctx: commands.Context, pet: str):
        """
        Buy a pet from the pet shop.
        """
        # get the user's balance
        balance = await self.bot.db.players.find_one({"_id": ctx.author.id})
        if balance is not None:
            balance = balance["coins"]
        else:
            return await ctx.send("You don't have any MineDollars.")
        # get the item
        pet = self.get_pet(pet.lower())
        if pet is None:
            return await ctx.send("That pet isn't in the shop.")
        # check if the user has enough money
        if pet["price"] > balance:
            return await ctx.send("You don't have enough MineDollars.")

        # ask the user what they want to name the pet
        await ctx.send(
            "What would you like to name your pet? (type `cancel` to cancel)"
        )
        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=30,
            )
        except asyncio.TimeoutError:
            return await ctx.send(
                "You took too long to respond, the transaction has been cancelled."
            )

        if msg.content.lower() == "cancel":
            return await ctx.send("Transaction cancelled.")

        # name length check
        if len(msg.content) > 15:
            return await ctx.send(
                "Your pet's name is too long, it must be 15 characters or less."
            )

        pets = await self.bot.db.players.find_one(
            {"_id": ctx.author.id, "pets": {"$exists": True}}
        )
        if pets is not None:
            pets = pets["pets"]
            # check if the user already has a pet with that name
            name_cases = list(all_casings(msg.content))
            if any(pet["name"] in name_cases for pet in pets):
                return await ctx.send(
                    "You already have a pet with that name, try again with a different name."
                )

        # subtract the price from the user's balance
        await self.bot.db.players.update_one(
            {"_id": ctx.author.id}, {"$inc": {"coins": int(-pet["price"])}}
        )
        # add the item to the user's pets
        pet = {"type": pet["type"], "name": msg.content, "level": 1, "exp": 0}
        # add the pet to the user's pets
        await self.bot.db.players.update_one(
            {"_id": ctx.author.id}, {"$push": {"pets": pet}}, upsert=True
        )
        # send a message
        await ctx.send(
            f"You bought a {pet['type']} and named it {pet['name']}! It is really happy."
        )

    @commands.group()
    async def pets(self, ctx: commands.Context):
        """
        Check your pets.
        """
        if ctx.invoked_subcommand is None:
            # get the user's pets
            pets = await self.bot.db.players.find_one({"_id": ctx.author.id})
            if pets is not None:
                pets = pets["pets"]
            else:
                return await ctx.send("You don't have any pets.")

            if not pets:  # incase the list exists but is empty
                return await ctx.send("You don't have any pets.")

            # set up the embed
            embed = discord.Embed(
                title=f"{ctx.author.name}'s pets",
                color=0x00FF00,  # green
            )
            # add the pets to the embed
            embed.description = ""
            for n, pet in enumerate(pets, start=1):
                embed.description += f"{n}. {pet['name']} ({pet['type'].title()})\n"
            # send the embed
            await ctx.send(embed=embed)

    @pets.command(usage="<pet>")
    async def pet(self, ctx: commands.Context, name: str):
        """
        Pet your pets.
        """
        # get the pet by name
        pet = await self.bot.db.players.find_one(
            {"_id": ctx.author.id, "pets.name": name}
        )
        if pet is None:
            return await ctx.send("You don't have a pet with that name.")
        else:
            pet = pet["pets"][0]

        # get the pet type
        pet_type = self.get_pet(pet["type"])
        # pet the pet
        pet_msg = random.choice(pet_type["pet_messages"])
        await ctx.send(pet_msg.format(pet["name"]))


def setup(bot):
    bot.add_cog(GamesAndEconomy(bot))
