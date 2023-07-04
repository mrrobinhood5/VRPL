import discord
from discord.ext import commands
from database import DBConnect
from pymongo.database import Database
from typing import Optional
from config import INTENTS, BOT_PREFIX, BOT_OWNER, COGS, TESTING_GUILD


class VRPLBot(commands.Bot):
    def __init__(self, *args, initial_extensions: list[str], db: Database, testing_guild: Optional[int], **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_extensions = initial_extensions
        self.db = db
        self.testing_guild = testing_guild
        self.settings = None

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        if self.testing_guild:
            guild = discord.Object(self.testing_guild)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)


bot = VRPLBot(command_prefix=BOT_PREFIX, description='VRPL Team Manager', intents=INTENTS, owner_id=int(BOT_OWNER),
              db=DBConnect().db, testing_guild=TESTING_GUILD, initial_extensions=['cogs.players', 'cogs.admin'])