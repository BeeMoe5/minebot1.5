import asyncio

import discord
from discord.ext import commands

from utils import all_casings, get_pet_data, get_item


class Shops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
    async def buy(self, ctx: commands.Context, *, item: str):
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
        item = get_item(ctx, item.lower())
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
    async def buy(self, ctx: commands.Context, *, pet: str):
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
        pet = get_pet_data(ctx, pet.lower())
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
