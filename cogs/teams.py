from discord.ext import commands
from discord import app_commands
from discord import Interaction
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from routers.teams import register_team, show_team
from classes.teams import TeamModel, NewTeamEmbed
from classes.team_player_mix import FullTeamModel, FullTeamEmbed, TeamCarousel
from classes.players import PlayerModel
from routers.players import show_player
from classes.errors import GenericErrorEmbed
from database import db_find_one_by_other, db_find_all, db_find_one, db_find_some
import json

# TODO: put the full team logic in its own function
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
        # get all team names
        team_list = await db_find_all('teams', amt=50)
        all_teams = []
        for team in team_list:
            team['captain'] = await db_find_one('players', str(team['captain']))
            team['co_captain'] = await db_find_one('players', str(team['co_captain']))
            player_list = await db_find_some('player_team_link', {'team': team['_id']}, exclude={'player': 1})
            player_list = [await db_find_one('players', player['player']) for player in player_list]
            team_players = [PlayerModel(**player) for player in player_list]
            team['members'] = team_players
            all_teams.append(team)
        all_teams = [FullTeamModel(**team) for team in all_teams]
        await inter.followup.send(embed=FullTeamEmbed(inter, all_teams[0]), view=TeamCarousel(all_teams))

    @app_commands.command(name='search', description='Search for a team')
    async def team_search(self, inter: Interaction, name: str):
        """ Search for a team """
        await inter.response.defer()
        team_list = await db_find_all('teams', amt=50)
        team_list = [team for team in team_list if name.lower() in team['name'].lower()]
        all_teams = []
        for team in team_list:
            team['captain'] = await db_find_one('players', str(team['captain']))
            team['co_captain'] = await db_find_one('players', str(team['co_captain']))
            player_list = await db_find_some('player_team_link', {'team': team['_id']}, exclude={'player': 1})
            player_list = [await db_find_one('players', player['player']) for player in player_list]
            team_players = [PlayerModel(**player) for player in player_list]
            team['members'] = team_players
            all_teams.append(team)
        all_teams = [FullTeamModel(**team) for team in all_teams]
        if all_teams:
            await inter.followup.send(embed=FullTeamEmbed(inter, all_teams[0]), view=TeamCarousel(all_teams))
        else:
            await inter.followup.send(f'No teams found')

    @app_commands.command(name='my_team', description='Display my team')
    async def team_me(self, inter: Interaction):
        """ Display your team """
        await inter.response.defer()
        if not (_ := await show_player(player_id=str(inter.user.id))):
            await inter.followup.send(f'You are not registered yet')

        me = PlayerModel(**_)
        if not (_ := await db_find_one_by_other('player_team_link', {'player': str(me.id)})):
            await inter.followup.send(f'You do not belong to a team yet')
        else:
            team = await db_find_one('teams', str(_['team']))

        team['captain'] = await db_find_one('players', str(team['captain']))
        team['co_captain'] = await db_find_one('players', str(team['co_captain']))
        player_list = await db_find_some('player_team_link', {'team': team['_id']}, exclude={'player': 1})
        player_list = [await db_find_one('players', player['player']) for player in player_list]
        team_players = [PlayerModel(**player) for player in player_list]
        team['members'] = team_players

        team = FullTeamModel(**team)
        await inter.followup.send(embed=FullTeamEmbed(inter, team))


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamCommands(bot))

