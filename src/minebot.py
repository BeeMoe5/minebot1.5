from discord.ext import commands


class MineBot(commands.Bot):
    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("------")
