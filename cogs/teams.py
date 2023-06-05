from discord.ext import commands
from discord import app_commands
from discord import Interaction

from fastapi.exceptions import HTTPException

from routers.teams import register_team, list_teams, get_team_members
from routers.players import show_player, get_player_team

from classes.teams import TeamModel, NewTeamEmbed
from classes.team_player_mix import FullTeamModel, FullTeamEmbed, TeamCarousel
from classes.players import PlayerModel

from classes.errors import GenericErrorEmbed
import json

# TODO: put the full team logic in its own function
class TeamCommands(commands.GroupCog, name='teams'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    async def build_full_team(self, team: TeamModel) -> FullTeamModel:
        team_captain = PlayerModel(**await show_player(str(team.captain)))
        if team.co_captain:
            team_co_captain = PlayerModel(**await show_player(str(team.co_captain)))
        else:
            team_co_captain = None
        team_members = [PlayerModel(**player) for player in await get_team_members(str(team.id))]

        full_team = {**team.dict(), **{
            "captain": team_captain,
            "co_captain": team_co_captain,
            "members": team_members
        }}
        return FullTeamModel(**full_team)

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
        team_list = await list_teams(50)
        if team_list:
            all_teams = [await self.build_full_team(TeamModel(**team)) for team in team_list]
            await inter.followup.send(embed=FullTeamEmbed(inter, all_teams[0]), view=TeamCarousel(all_teams))
        else:
            await inter.followup.send(f'No teams Found')

    @app_commands.command(name='search', description='Search for a team')
    async def team_search(self, inter: Interaction, name: str):
        """ Search for a team """
        await inter.response.defer()
        team_list = await list_teams(50)
        team_list = [team for team in team_list if name.lower() in team['name'].lower()]
        if team_list:
            all_teams = [await self.build_full_team(TeamModel(**team)) for team in team_list]
            await inter.followup.send(embed=FullTeamEmbed(inter, all_teams[0]), view=TeamCarousel(all_teams))
        else:
            await inter.followup.send(f'No teams found')

    @app_commands.command(name='my_team', description='Display my team')
    async def team_me(self, inter: Interaction):
        """ Display your team """
        await inter.response.defer()
        if not (_ := await show_player(player_id=str(inter.user.id))):
            await inter.followup.send(f'You are not registered yet')

        try:
            team = await get_player_team(_['_id'])
        except HTTPException as e:
            await inter.followup.send(embed=GenericErrorEmbed(inter.user, e))

        full_team = await self.build_full_team(TeamModel(**team))
        await inter.followup.send(embed=FullTeamEmbed(inter, full_team))


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamCommands(bot))

