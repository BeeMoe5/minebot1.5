import typing

import discord
from discord.ext import commands

guild_state = {}


def rainbow(
    guild_id,
):  # outside the class because the class is deep copied internally, which would reset the color every time the command
    # is run.

    colors = (0xFF0000, 0xFFA500, 0xFFFF00, 0x008000, 0x0000FF, 0x4B0082, 0x8A2BE2)
    if guild_id not in guild_state.keys():
        guild_state[guild_id] = 0  # start at the first color

    current_color = colors[guild_state[guild_id]]
    guild_state[guild_id] += 1  # increment the color

    if guild_state[guild_id] >= len(colors):
        guild_state[guild_id] = 0  # reset to 0 if we've gone through all the colors
    return current_color


class MineBotHelp(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self._embed: typing.Optional[discord.Embed] = None

    @property
    def embed(self):
        if self._embed is None:
            prefix = self.context.prefix
            color = rainbow(self.context.guild.id)
            self._embed = discord.Embed(
                title="Help",
                description=f"Use `{prefix}help [command]` to get more info about a command.",
                color=color,
            )
        return self._embed

    async def send_bot_help(
        self, mapping
    ):  # this is called when help is invoked without arguments
        # build embed
        cmds = sorted(self.context.bot.commands, key=lambda c: c.name)
        self.embed.description += "\n" + ", ".join(f"{self.context.prefix}{c.name}" for c in cmds)
        await self.context.send(embed=self.embed)

    async def send_cog_help(
        self, cog
    ):  # this is called when help is invoked with a cog as an argument
        # get cog object
        cog = self.context.get_cog(cog)
        if cog is None:
            return await self.send_error_message(f"Cog `{cog}` not found.")
        # get command list
        cmds = sorted(cog.get_commands(), key=lambda c: c.name)
        # build embed
        self.embed.title = f"{cog.qualified_name} Commands"
        description = ", ".join(f"{self.context.prefix}{c.name}" for c in cmds)
        self.embed.description = description
        # send embed
        destination = self.get_destination()
        await destination.send(embed=self.embed)

    async def send_command_help(self, command):
        # build embed
        self.embed.title = f"{command.qualified_name} {command.signature}"
        self.embed.description = command.help
        # send embed
        destination = self.get_destination()
        await destination.send(embed=self.embed)

    async def send_error_message(self, error_message):
        destination = self.get_destination()
        await destination.send(error_message)
