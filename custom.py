import discord
from discord.ext import commands
from database import Database
from typing import Optional
from config import TESTING_GUILD


class VRPLBot(commands.Bot):
    def __init__(self, *args, initial_extensions: list[str] = None, db: Database = Database(), testing_guild: int = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_extensions = initial_extensions
        self.db = db
        self.testing_guild = testing_guild
        self.settings = None  # This will probably be a BeanieDocumentModel

    async def setup_hook(self) -> None:
        if self.initial_extensions:
            for extension in self.initial_extensions:
                await self.load_extension(extension)
        else:
            pass

    async def load_extensions(self, extensions: list[str]):
        for extension in extensions:
            await self.load_extension(extension)

        # This copies the tree every restart. Disabled because there's a command for it instead
        # if self.testing_guild:
        #     guild = discord.Object(self.testing_guild)
        #     self.tree.copy_global_to(guild=guild)
        #     await self.tree.sync(guild=guild)

    def refresh_settings(self):
        self.settings = self.settings.refresh()


bot = VRPLBot(esting_guild=TESTING_GUILD, command_prefix='.', intents=discord.Intents.default())

