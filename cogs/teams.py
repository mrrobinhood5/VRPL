from discord.ext import commands
from discord import app_commands
from discord import Interaction


class TeamCommands(commands.GroupCog, name='teams'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name='list', description='List all teams')
    async def teams_view_all(self, inter: Interaction):
        """ List all teams """
        await inter.response.defer()

    @app_commands.command(name='search', description='Search for a team')
    async def team_search(self, inter: Interaction):
        """ Search for a team """
        await inter.response.defer()

    @app_commands.command(name='my_team', description='Display my team')
    async def team_me(self, inter: Interaction):
        """ Display your team """
        await inter.response.defer()


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamCommands(bot))
