import random
from pathlib import Path

from discord.ext import commands

from help import MineBotHelp


class MineBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help_command = MineBotHelp()
        self.is_loaded = False

    def load_cogs(self):
        # get cog directory
        cogs_dir = Path(__file__).parent / "cogs"
        # get every file in the directory
        for file in cogs_dir.iterdir():
            # get the file name
            file_name = file.name
            # .py file verification
            if file_name.endswith(".py"):
                self.load_extension(f"cogs.{file_name[:-3]}")
                print(f"Loaded {file_name}")

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("------")
        # cog loading
        if not self.is_loaded:
            self.load_cogs()
            self.is_loaded = True

    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.CommandNotFound):
            return
        raise exception
