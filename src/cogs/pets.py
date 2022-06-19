import random

import discord
from discord.ext import commands

from utils import cooldown, get_pet_data


class Pets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
    async def pet(self, ctx: commands.Context, *, name: str):
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
            # find the pet in the list
            pet = next(
                (p for p in pet["pets"] if p["name"] == name), None
            )  # get the pet
            if pet is None:
                return await ctx.send("You don't have a pet with that name.")

        # get the pet type
        pet_type = get_pet_data(ctx, pet["type"])
        # pet the pet
        pet_msg = random.choice(pet_type["pet_messages"])
        await ctx.send(pet_msg.format(pet["name"]))

    # ratelimit the pet command
    @cooldown(days=1)
    @pets.command(usage="<pet>")
    async def feed(self, ctx: commands.Context, *, name: str):
        """
        Feed your pets.
        """
        # get the pet by name
        pet = await self.bot.db.players.find_one(
            {"_id": ctx.author.id, "pets.name": name}
        )
        if pet is None:
            return await ctx.send("You don't have a pet with that name.")
        else:
            pet = pet["pets"][0]

        await ctx.send(
            f"You feed {pet['name']}! {pet['name']} is satisfied and earns 5 xp, and you earn 3 coins!"
        )
        # add xp to the pet and add coins to the user
        await self.bot.db.players.update_one(
            {"_id": ctx.author.id, "pets.name": name},
            {"$inc": {"pets.$.exp": 5, "coins": 3}},
        )


def setup(bot):
    bot.add_cog(Pets(bot))
