from discord.ext import commands
from discord import app_commands
from discord import Interaction
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from routers.teams import register_team, show_team
from classes.teams import TeamModel, NewTeamEmbed, TeamCarousel, FullTeamEmbed
from routers.players import show_player
from classes.errors import GenericErrorEmbed
from database import db_get_full_team
import json


class TeamCommands(commands.GroupCog, name='teams'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name='register', description='Register a team')
    async def team_register(self, inter: Interaction, name: str, motto: str, logo: str = None):
        """ Register a team """
        await inter.response.defer()

        try:
            captain = await show_player(str(inter.user.id))
        except HTTPException as e:
            await inter.followup.send(embed=GenericErrorEmbed(inter.user, e))

        team = TeamModel(name=name, team_motto=motto, team_logo=logo, captain=captain['_id'])

        try:
            team = await register_team(team)
        except HTTPException as e:
            await inter.followup.send(embed=GenericErrorEmbed(inter.user, e))
        else:
            created_team = json.loads(team.body.decode())
            await inter.followup.send(content='Registration Complete', embed=NewTeamEmbed(inter, created_team))

    @app_commands.command(name='list', description='List all teams')
    async def teams_view_all(self, inter: Interaction):
        """ List all teams """
        await inter.response.defer()
        teams = await db_get_full_team()
        await inter.followup.send(embed=FullTeamEmbed(inter, teams[0]), view=TeamCarousel(teams))

    @app_commands.command(name='search', description='Search for a team')
    async def team_search(self, inter: Interaction, name: str):
        """ Search for a team """
        await inter.response.defer()
        teams = await db_get_full_team()
        teams = [team for team in teams if name in team['name']]
        await inter.followup.send(embed=FullTeamEmbed(inter, teams[0]), view=TeamCarousel(teams))

    @app_commands.command(name='my_team', description='Display my team')
    async def team_me(self, inter: Interaction):
        """ Display your team """
        await inter.response.defer()


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamCommands(bot))

