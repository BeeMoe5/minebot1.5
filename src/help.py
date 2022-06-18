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
        categories = {}  # also includes commands without a category
        # get every command object, excluding hidden commands, and group them by category
        for cmd in self.context.bot.commands:
            if cmd.hidden:
                continue
            # category aka cog
            # if cmd is uncategorized (no cog), add it to the uncategorized category
            if cmd.cog is None:
                category = "Uncategorized"
            else:
                category = cmd.cog.qualified_name
            # add the command to the category
            if category not in categories:
                categories[category] = []
            categories[category].append(cmd)
        # build embed
        # sort the categories
        categories = sorted(categories.items(), key=lambda c: c[0])
        # for each category, build a string of commands and add it to the embed
        for category, cmds in categories:
            # build string of commands
            cmd_string = ", ".join(c.name for c in cmds)
            # add the category and commands to the embed
            self.embed.add_field(name=category, value=cmd_string, inline=False)
        # send embed
        destination = self.get_destination()
        await destination.send(embed=self.embed)

    async def send_cog_help(
        self, cog
    ):  # this is called when help is invoked with a cog as an argument

        # get command list, excluding hidden commands
        cmds = sorted(
            [c for c in cog.get_commands() if not c.hidden], key=lambda c: c.name
        )
        # build embed
        self.embed.title = f"{cog.qualified_name} Commands"
        description = ", ".join(c.name for c in cmds)
        self.embed.description = description
        # send embed
        destination = self.get_destination()
        await destination.send(embed=self.embed)

    async def send_command_help(self, command):
        # build embed
        self.embed.title = (
            command.name + "|".join(command.aliases) + f" {command.signature}"
        )
        self.embed.description = command.help
        # send embed
        destination = self.get_destination()
        await destination.send(embed=self.embed)
        
    async def send_group_help(self, group):
        # build embed
        self.embed.title = self.context.prefix + group.name
        self.embed.description = group.help + "\n\n*this is a group command*"
        # for each command in the group, add it to the embed
        for cmd in group.commands:
            self.embed.add_field(
                name=self.context.prefix + cmd.name + "|".join(cmd.aliases) + f" {cmd.signature}", value=cmd.help, inline=False
            )
        # send embed
        destination = self.get_destination()
        await destination.send(embed=self.embed)

    async def send_error_message(self, error_message):
        destination = self.get_destination()
        await destination.send(error_message)

    def command_not_found(self, string):
        return f"Command or category `{string}` not found."
