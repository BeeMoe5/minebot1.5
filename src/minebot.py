import json
import random
from pathlib import Path

from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient

from help import MineBotHelp


class MineBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help_command = MineBotHelp()
        self.cogs_loaded = False
        self.db_connected = False
        self.shop_loaded = False
        self.shop_items = None
        self.db = None

    def load_cogs(self):
        if not self.cogs_loaded:
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

    def connect_db(self):
        # connect to mongodb
        if not self.db:
            client = AsyncIOMotorClient("mongodb://localhost:27017/")
            self.db = client.minebot

    def load_shop(self):
        # get the shop items
        if not self.shop_loaded:
            with open(Path(__file__).parent / "shop.json", "r") as shop_file:
                self.shop_items = json.load(shop_file)

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("------")
        # cog loading
        self.load_cogs()
        # db connection
        self.connect_db()
        # shop loading
        self.load_shop()

    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.CommandNotFound):
            return
        raise exception

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)
        # change the random seed for each message
        random.seed(message.id)
