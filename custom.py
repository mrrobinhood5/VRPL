import discord
from discord.ext import commands
from config import TESTING_GUILD
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
        self.ae: AdminEngine = AdminEngine()
        self.ge: GameEngine = GameEngine()
        self.pe: PlayerEngine = PlayerEngine()
        self.te: TeamEngine = TeamEngine()

bot = VRPLBot(testing_guild=TESTING_GUILD, command_prefix='.', intents=discord.Intents.all())

