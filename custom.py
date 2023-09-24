import discord
from discord.ext import commands

from engines import *


class VRPLBot(commands.Bot):
    def __init__(self, *args, initial_extensions: list[str] = None, testing_guild: int = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_extensions = initial_extensions
        self.testing_guild = testing_guild

    async def load_extensions(self, extensions: list[str]):
        for extension in extensions:
            await self.load_extension(extension)

    async def load_engines(self, engines: Optional[list[str]] = None):
        # TODO: make this automated like when loading beanie models
        self.ae: AdminEngine = AdminEngine(bot=self)
        self.ge: GameEngine = GameEngine(bot=self)
        self.pe: PlayerEngine = PlayerEngine(bot=self)
        self.te: TeamEngine = TeamEngine(bot=self)



